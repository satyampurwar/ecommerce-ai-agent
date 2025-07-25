"""Utilities for creating and populating the SQLite database."""

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

def create_db_and_tables(database_url: str = DATABASE_URL):
    """Create the SQLite database and all ORM tables if needed.

    Parameters
    ----------
    database_url : str, optional
        Connection string for the database.

    Returns
    -------
    sqlalchemy.engine.Engine
        Engine connected to the created database.
    """
    print(f"[DB_SETUP] Creating engine for DB at: {database_url}")
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    with engine.connect() as conn:
        # SQLite does not enforce FKs by default
        print("[DB_SETUP] Enabling SQLite foreign key constraints ...")
        conn.execute(text("PRAGMA foreign_keys=ON"))
    print("[DB_SETUP] Creating all tables (if not exist) ...")
    Base.metadata.create_all(engine)
    print("[DB_SETUP] All tables should now exist.")
    return engine

def import_csv_to_db(engine, table_class, csv_path):
    """Load a CSV file into the given table.

    Parameters
    ----------
    engine : sqlalchemy.engine.Engine
        Database engine.
    table_class : DeclarativeMeta
        ORM model representing the table.
    csv_path : str
        Path to the CSV file.
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
        # Convert CSV string values to appropriate Python types for SQLAlchemy
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
            # Bulk insert all rows for efficiency
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

def populate_database(engine, data_folder: str = DATA_FOLDER, table_map=CSV_TABLE_MAP):
    """Populate all tables from CSV files.

    Parameters
    ----------
    engine : sqlalchemy.engine.Engine
        Database engine.
    data_folder : str, optional
        Directory containing CSV files.
    table_map : dict, optional
        Mapping from table key to CSV filename.
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
    """Return a new SQLAlchemy session bound to ``engine``.

    Parameters
    ----------
    engine : sqlalchemy.engine.Engine
        Engine to bind the session to.

    Returns
    -------
    sqlalchemy.orm.Session
        Configured session instance.
    """
    Session = sessionmaker(bind=engine)
    return Session()


def setup_database():
    """Create the database and load data from CSV files.

    Returns
    -------
    sqlalchemy.engine.Engine
        Engine connected to the populated database.
    """
    engine = create_db_and_tables()
    populate_database(engine)
    return engine


def main():
    """Command-line entry point for manual execution."""

    print("[MAIN] Creating database and importing CSV files ...")
    setup_database()
    print("[MAIN] Database setup complete.")


if __name__ == "__main__":
    main()
