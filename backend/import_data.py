import json
import logging
from datetime import datetime
from pathlib import Path

from services.import_service import ImportReport, scan_and_import
from utils.logger import configure_logging


def format_summary(report: ImportReport) -> str:
    lines = [
        "Import Summary:",
        f"  Total files processed: {report.total_files_processed}",
        f"  Total records inserted: {report.total_records_inserted}",
        f"  Total duplicates skipped: {report.total_duplicates_skipped}",
        f"  Total files failed: {report.total_files_failed}",
        "Collection statistics:",
    ]

    for collection_name, stats in sorted(report.collection_stats.items()):
        lines.append(f"  - {collection_name}:")
        lines.append(f"      files_processed: {stats['files_processed']}")
        lines.append(f"      records_inserted: {stats['records_inserted']}")
        lines.append(f"      duplicates_skipped: {stats['duplicates_skipped']}")

    if report.failed_files:
        lines.append("Failed files:")
        for failed_file in report.failed_files:
            lines.append(f"  - {failed_file}")

    return "\n".join(lines)


def main() -> None:
    configure_logging()
    logger = logging.getLogger("import_data")
    project_root = Path(__file__).resolve().parent

    logger.info("Starting dataset import from backend folder: %s", project_root)
    report = scan_and_import(project_root)

    report_file = project_root / f"import_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        report_file.write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("Import report written to %s", report_file)
    except Exception as exc:
        logger.error("Unable to write import report: %s", exc)

    summary = format_summary(report)
    print(summary)
    logger.info("Import finished")


if __name__ == "__main__":
    main()
