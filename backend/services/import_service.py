import hashlib
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from pymongo.errors import BulkWriteError
from tqdm import tqdm

from config import db
from services.db import ensure_import_index


SUPPORTED_JSON_EXTENSIONS = {".json"}
IGNORE_FILENAMES = {"thumbs.db"}


@dataclass
class ImportReport:
    total_files_processed: int = 0
    total_records_inserted: int = 0
    total_duplicates_skipped: int = 0
    total_files_failed: int = 0
    collection_stats: Dict[str, Dict[str, int]] = None
    failed_files: List[str] = None

    def __post_init__(self):
        self.collection_stats = self.collection_stats or {}
        self.failed_files = self.failed_files or []

    def record_collection(self, collection_name: str, inserted: int, duplicates: int) -> None:
        stats = self.collection_stats.setdefault(collection_name, {
            "files_processed": 0,
            "records_inserted": 0,
            "duplicates_skipped": 0,
        })
        stats["files_processed"] += 1
        stats["records_inserted"] += inserted
        stats["duplicates_skipped"] += duplicates

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def get_collection_name(source_path: Path, dataset_root: Path) -> str:
    relative_path = source_path.relative_to(dataset_root)
    first_folder = relative_path.parts[0].lower()
    if first_folder == "dataset":
        parts = relative_path.parts[1:2]
        collection_name = parts[0].lower() if parts else "unknown"
    else:
        collection_name = "metadata"

    return collection_name.replace(" ", "_")


def scan_json_files(root_path: Path) -> Iterable[Path]:
    for file_path in root_path.rglob("*"):
        if file_path.is_file() and file_path.name.lower() not in IGNORE_FILENAMES:
            if file_path.suffix.lower() in SUPPORTED_JSON_EXTENSIONS:
                yield file_path


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        raw_text = path.read_text(encoding="utf-8")
        return json.loads(raw_text)
    except json.JSONDecodeError as exc:
        logging.warning("Skipping corrupted JSON %s: %s", path, exc)
        return None
    except Exception as exc:
        logging.error("Failed to read %s: %s", path, exc)
        return None


def compute_document_hash(document: Dict[str, Any]) -> str:
    canonical_json = json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def normalize_document(document: Dict[str, Any], source_file: str, source_path: str, collection_name: str) -> Dict[str, Any]:
    normalized = dict(document)
    normalized["sourceFile"] = source_file
    normalized["sourcePath"] = source_path
    normalized["collectionName"] = collection_name
    normalized["importedAt"] = datetime.utcnow().isoformat() + "Z"
    normalized["document_hash"] = compute_document_hash(document)
    return normalized


def prepare_documents(raw_data: Any, source_file: str, source_path: str, collection_name: str) -> List[Dict[str, Any]]:
    documents: List[Dict[str, Any]] = []

    if isinstance(raw_data, dict):
        documents.append(normalize_document(raw_data, source_file, source_path, collection_name))
    elif isinstance(raw_data, list):
        for item in raw_data:
            if isinstance(item, dict):
                documents.append(normalize_document(item, source_file, source_path, collection_name))
            else:
                logging.warning("Skipping non-dictionary item in %s", source_file)
    else:
        logging.warning("Unsupported JSON structure in %s", source_file)

    return documents


def insert_documents(collection_name: str, documents: List[Dict[str, Any]]) -> Dict[str, int]:
    if not documents:
        return {"inserted_count": 0, "duplicate_count": 0}

    collection = db[collection_name]
    ensure_import_index(collection_name)

    inserted_count = 0
    duplicate_count = 0
    try:
        result = collection.insert_many(documents, ordered=False)
        inserted_count = len(result.inserted_ids)
    except BulkWriteError as exc:
        write_errors = exc.details.get("writeErrors", [])
        duplicate_count = sum(1 for error in write_errors if error.get("code") in {11000, 11001, 12582})
        inserted_count = len(documents) - duplicate_count
        logging.warning("Bulk insert partial success in %s: inserted=%s duplicates=%s", collection_name, inserted_count, duplicate_count)
    except Exception as exc:
        logging.error("Bulk insert failed for collection %s: %s", collection_name, exc)
        raise

    return {"inserted_count": inserted_count, "duplicate_count": duplicate_count}


def scan_and_import(project_root: Path) -> ImportReport:
    logger = logging.getLogger("import_service")
    primary_root = project_root.parent / "Cut_Off_Project" / "Cut_Off_Project"
    fallback_root = project_root.parent / "Cut_Off_Project"
    report = ImportReport()

    if primary_root.exists():
        source_root = primary_root
    elif fallback_root.exists():
        source_root = fallback_root
    else:
        logger.error("Dataset source folder does not exist: %s or %s", primary_root, fallback_root)
        return report

    json_files = list(scan_json_files(source_root))
    logger.info("Found %s JSON files for import", len(json_files))

    for file_path in tqdm(json_files, desc="Importing JSON files", unit="file"):
        report.total_files_processed += 1
        raw_data = load_json(file_path)
        if raw_data is None:
            report.total_files_failed += 1
            report.failed_files.append(str(file_path))
            continue

        collection_name = get_collection_name(file_path, source_root)
        source_file = file_path.name
        source_path = str(file_path.parent.relative_to(source_root)).replace("\\", "/")
        documents = prepare_documents(raw_data, source_file, source_path, collection_name)

        try:
            stats = insert_documents(collection_name, documents)
            report.total_records_inserted += stats["inserted_count"]
            report.total_duplicates_skipped += stats["duplicate_count"]
            report.record_collection(collection_name, stats["inserted_count"], stats["duplicate_count"])
        except Exception:
            report.total_files_failed += 1
            report.failed_files.append(str(file_path))

    return report
