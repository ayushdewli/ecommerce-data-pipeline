import pandas as pd
from pymongo import MongoClient
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DATA_PATH = os.getenv("DATA_PATH", "/opt/data")

def ingest_collection(client, db_name, collection_name, csv_file):
    db = client[db_name]
    collection = db[collection_name]

    filepath = os.path.join(DATA_PATH, csv_file)
    if not os.path.exists(filepath):
        logger.warning(f"File not found: {filepath}")
        return 0

    df = pd.read_csv(filepath)
    collection.drop()  # clear old data before re-loading
    records = df.to_dict(orient="records")

    if records:
        collection.insert_many(records)
        logger.info(f"Inserted {len(records)} rows into {collection_name}")

    return len(records)

def run_ingestion():
    client = MongoClient(MONGO_URI)

    files = {
        "orders":               "olist_orders_dataset.csv",
        "order_items":          "olist_order_items_dataset.csv",
        "products":             "olist_products_dataset.csv",
        "customers":            "olist_customers_dataset.csv",
        "reviews":              "olist_order_reviews_dataset.csv",
        "payments":             "olist_order_payments_dataset.csv",
        "sellers":              "olist_sellers_dataset.csv",
        "category_translation": "product_category_name_translation.csv",
    }

    total = 0
    for name, csv_file in files.items():
        total += ingest_collection(client, "olist_raw", name, csv_file)

    logger.info(f"Done. Total records loaded: {total}")
    client.close()

if __name__ == "__main__":
    run_ingestion()