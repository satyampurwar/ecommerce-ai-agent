import os
import csv
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import DateTime, Integer, Float, SmallInteger
from config import DATABASE_FILE, DATABASE_URL, DATA_FOLDER, CSV_TABLE_MAP
from db.models import (
    Base,
    OlistCustomersDataset,
    OlistOrdersDataset,
    OlistOrderItemsDataset,
    OlistOrderPaymentsDataset,
    OlistOrderReviewsDataset,
    OlistProductsDataset,
    OlistSellersDataset,
    OlistGeolocationDataset,
    ProductCategoryNameTranslation,
)

def create_db_and_tables(database_url=DATABASE_URL):
    """
    Create the SQLite database file and all tables using ORM models, if not already present.
    Enables foreign-key enforcement for SQLite.
    """
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=ON"))
    # Create all tables based on ORM metadata (FKs, PKs, relationships are preserved)
    Base.metadata.create_all(engine)
    return engine

def import_csv_to_db(engine, table_class, csv_path):
    """
    Import a CSV file to the database using the provided ORM table class.
    Uses ORM bulk_save_objects for correct relationships.
    """
    if not os.path.exists(csv_path):
        print(f"Warning: CSV {csv_path} not found. Skipping import for {table_class.__tablename__}.")
        return

    expected_cols = [c.name for c in table_class.__table__.columns]
    pk_cols = [c.name for c in table_class.__table__.primary_key.columns]

    Session = sessionmaker(bind=engine)
    session = Session()
    objects = []
    seen_keys = set()

    def parse_value(val, column):
        if val in ("", None, "NaN", "NaT"):  # treat empty strings as None
            return None
        if isinstance(column.type, DateTime):
            try:
                return datetime.fromisoformat(val)
            except ValueError:
                for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d"):
                    try:
                        return datetime.strptime(val, fmt)
                    except ValueError:
                        continue
                return None
        if isinstance(column.type, (Integer, SmallInteger)):
            try:
                return int(float(val))
            except ValueError:
                return None
        if isinstance(column.type, Float):
            try:
                return float(val)
            except ValueError:
                return None
        return val

    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        missing_cols = set(expected_cols) - set(reader.fieldnames)
        if missing_cols:
            print(
                f"CSV {csv_path} missing columns {missing_cols}. Skipping import for {table_class.__tablename__}."
            )
            session.close()
            return

        for raw_row in reader:
            key = tuple(raw_row[col] for col in pk_cols)
            if key in seen_keys:
                continue
            seen_keys.add(key)

            row = {}
            for column in table_class.__table__.columns:
                row[column.name] = parse_value(raw_row.get(column.name), column)

            try:
                obj = table_class(**row)
                objects.append(obj)
            except Exception as e:
                print(f"Row skipped in {table_class.__tablename__}: {row} -- {e}")

    try:
        if objects:
            session.bulk_save_objects(objects)
            session.commit()
            print(f"Imported {len(objects)} records into {table_class.__tablename__}")
        else:
            print(f"No valid records found in {csv_path}.")
    except Exception as e:
        session.rollback()
        print(f"Failed to insert records into {table_class.__tablename__}: {e}")
    finally:
        session.close()

def populate_database(engine, data_folder=DATA_FOLDER, table_map=CSV_TABLE_MAP):
    """
    Populates all ORM tables from CSVs in the data folder.
    Only appends data; will not overwrite existing rows.
    The insertion order is set to maintain referential integrity.
    """
    # Ordered by dependencies (parents first, then children)
    table_sequence = [
        (OlistCustomersDataset, 'olist_customers_dataset'),
        (OlistGeolocationDataset, 'olist_geolocation_dataset'),
        (OlistProductsDataset, 'olist_products_dataset'),
        (OlistSellersDataset, 'olist_sellers_dataset'),
        (OlistOrdersDataset, 'olist_orders_dataset'),
        (OlistOrderItemsDataset, 'olist_order_items_dataset'),
        (OlistOrderPaymentsDataset, 'olist_order_payments_dataset'),
        (OlistOrderReviewsDataset, 'olist_order_reviews_dataset'),
        (ProductCategoryNameTranslation, 'product_category_name_translation'),
    ]
    for table_class, table_key in table_sequence:
        csv_file = table_map.get(table_key)
        if not csv_file:
            continue
        csv_path = os.path.join(data_folder, csv_file)
        import_csv_to_db(engine, table_class, csv_path)

def get_session(engine):
    """
    Returns a new SQLAlchemy ORM session for database operations.
    """
    Session = sessionmaker(bind=engine)
    return Session()

# --- Example usage (in main.py or interactive session) ---
if __name__ == "__main__":
    # 1. Create DB and tables (safe if run multiple times)
    engine = create_db_and_tables()
    # 2. Populate tables from CSVs
    populate_database(engine)
    # 3. Create session for querying
    session = get_session(engine)
    # Example: Fetch 5 orders
    orders = session.query(OlistOrdersDataset).limit(5).all()
    for order in orders:
        print(order.order_id, order.customer_id, order.order_status)
    session.close()
