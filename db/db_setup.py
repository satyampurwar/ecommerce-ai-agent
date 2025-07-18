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
    print(f"[DB_SETUP] Creating engine for DB at: {database_url}")
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    with engine.connect() as conn:
        print("[DB_SETUP] Enabling SQLite foreign key constraints ...")
        conn.execute(text("PRAGMA foreign_keys=ON"))
    print("[DB_SETUP] Creating all tables (if not exist) ...")
    Base.metadata.create_all(engine)
    print("[DB_SETUP] All tables should now exist.")
    return engine

def import_csv_to_db(engine, table_class, csv_path):
    """
    Import a CSV file to the database using the provided ORM table class.
    Uses ORM bulk_save_objects for correct relationships.
    """
    print(f"[IMPORT] Attempting to import {csv_path} into table '{table_class.__tablename__}' ...")

    if not os.path.exists(csv_path):
        print(f"[IMPORT][WARNING] CSV {csv_path} not found. Skipping import for '{table_class.__tablename__}'.")
        return

    expected_cols = [c.name for c in table_class.__table__.columns]
    pk_cols = [c.name for c in table_class.__table__.primary_key.columns]
    print(f"[IMPORT] Table '{table_class.__tablename__}' expects columns: {expected_cols}")
    print(f"[IMPORT] Table '{table_class.__tablename__}' primary key columns: {pk_cols}")

    Session = sessionmaker(bind=engine)
    session = Session()
    objects = []
    seen_keys = set()

    def parse_value(val, column):
        if val in ("", None, "NaN", "NaT"):
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

    try:
        with open(csv_path, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
            print(f"[IMPORT] Columns found in CSV: {reader.fieldnames}")

            missing_cols = set(expected_cols) - set(reader.fieldnames)
            if missing_cols:
                print(
                    f"[IMPORT][ERROR] CSV {csv_path} missing columns {missing_cols}. Skipping import for '{table_class.__tablename__}'."
                )
                session.close()
                return

            row_count = 0
            for raw_row in reader:
                key = tuple(raw_row[col] for col in pk_cols)
                if key in seen_keys:
                    print(f"[IMPORT][SKIP] Duplicate key found (skipping): {key}")
                    continue
                seen_keys.add(key)

                row = {}
                for column in table_class.__table__.columns:
                    row[column.name] = parse_value(raw_row.get(column.name), column)

                try:
                    obj = table_class(**row)
                    objects.append(obj)
                    row_count += 1
                    if row_count <= 2:  # Only print for the first couple of rows for brevity
                        print(f"[IMPORT] Example row {row_count}: {row}")
                except Exception as e:
                    print(f"[IMPORT][SKIP] Row skipped in '{table_class.__tablename__}': {row} -- {e}")

            print(f"[IMPORT] Finished reading CSV. Prepared {len(objects)} objects for bulk insert.")

        if objects:
            session.bulk_save_objects(objects)
            session.commit()
            print(f"[IMPORT][SUCCESS] Imported {len(objects)} records into '{table_class.__tablename__}'.")
        else:
            print(f"[IMPORT][WARNING] No valid records found in {csv_path} for table '{table_class.__tablename__}'.")
    except Exception as e:
        session.rollback()
        print(f"[IMPORT][FAILURE] Failed to insert records into '{table_class.__tablename__}': {e}")
    finally:
        session.close()
        print(f"[IMPORT] Session closed for table '{table_class.__tablename__}'.")

def populate_database(engine, data_folder=DATA_FOLDER, table_map=CSV_TABLE_MAP):
    """
    Populates all ORM tables from CSVs in the data folder.
    Only appends data; will not overwrite existing rows.
    The insertion order is set to maintain referential integrity.
    """
    print("[POPULATE] Populating database with CSVs ...")
    print(f"[POPULATE] Using data folder: {data_folder}")
    print(f"[POPULATE] Table map: {table_map}")
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
            print(f"[POPULATE][WARNING] No CSV mapping for '{table_key}', skipping ...")
            continue
        csv_path = os.path.join(data_folder, csv_file)
        import_csv_to_db(engine, table_class, csv_path)
    print("[POPULATE] All CSV imports attempted.")

def get_session(engine):
    """
    Returns a new SQLAlchemy ORM session for database operations.
    """
    Session = sessionmaker(bind=engine)
    return Session()

# --- Example usage (for standalone testing) ---
if __name__ == "__main__":
    print("[MAIN] Running db_setup.py directly (standalone test mode)")
    engine = create_db_and_tables()
    print("[MAIN] Now populating database from CSV files ...")
    populate_database(engine)
    session = get_session(engine)
    print("[MAIN] Example: Fetch 5 orders from 'olist_orders_dataset':")
    try:
        orders = session.query(OlistOrdersDataset).limit(5).all()
        for order in orders:
            print("Order:", order.order_id, order.customer_id, order.order_status)
    except Exception as e:
        print(f"[MAIN][ERROR] Could not query orders: {e}")
    finally:
        session.close()