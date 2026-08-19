import logging

from config import db


def ensure_import_index(collection_name: str) -> None:
    collection = db[collection_name]
    logging.info("Ensuring unique document index on collection %s", collection_name)
    collection.create_index(
        [("document_hash", 1)],
        unique=True,
        name="unique_document_hash",
        background=True,
    )


def get_collection(collection_name: str):
    return db[collection_name]
