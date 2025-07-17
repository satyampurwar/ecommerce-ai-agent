import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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
    """
    engine = create_engine(database_url)
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

    df = pd.read_csv(csv_path)
    # Remove duplicates by PK to avoid IntegrityError (adjust as needed)
    df = df.drop_duplicates()
    # NaN to None for SQLAlchemy
    df = df.where(pd.notnull(df), None)

    data = df.to_dict(orient='records')
    # Bulk insert via ORM
    Session = sessionmaker(bind=engine)
    session = Session()
    objects = []
    for row in data:
        try:
            obj = table_class(**row)
            objects.append(obj)
        except Exception as e:
            print(f"Row skipped in {table_class.__tablename__}: {row} -- {e}")
            continue
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