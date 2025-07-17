from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey

Base = declarative_base()

class OlistCustomersDataset(Base):
    __tablename__ = 'olist_customers_dataset'
    customer_id = Column(String, primary_key=True)
    customer_unique_id = Column(String)
    customer_zip_code_prefix = Column(Integer)
    customer_city = Column(String)
    customer_state = Column(String)
    # Relationships
    orders = relationship('OlistOrdersDataset', back_populates='customer')

class OlistOrdersDataset(Base):
    __tablename__ = 'olist_orders_dataset'
    order_id = Column(String, primary_key=True)
    customer_id = Column(String, ForeignKey('olist_customers_dataset.customer_id'))
    order_status = Column(String)
    order_purchase_timestamp = Column(DateTime)
    order_approved_at = Column(DateTime)
    order_delivered_carrier_date = Column(DateTime)
    order_delivered_customer_date = Column(DateTime)
    order_estimated_delivery_date = Column(DateTime)
    # Relationships
    customer = relationship('OlistCustomersDataset', back_populates='orders')
    order_items = relationship('OlistOrderItemsDataset', back_populates='order')
    order_payments = relationship('OlistOrderPaymentsDataset', back_populates='order')
    order_reviews = relationship('OlistOrderReviewsDataset', back_populates='order')

class OlistOrderItemsDataset(Base):
    __tablename__ = 'olist_order_items_dataset'
    order_id = Column(String, ForeignKey('olist_orders_dataset.order_id'), primary_key=True)
    order_item_id = Column(Integer, primary_key=True)
    product_id = Column(String, ForeignKey('olist_products_dataset.product_id'))
    seller_id = Column(String, ForeignKey('olist_sellers_dataset.seller_id'))
    shipping_limit_date = Column(DateTime)
    price = Column(Float)
    freight_value = Column(Float)
    # Relationships
    order = relationship('OlistOrdersDataset', back_populates='order_items')
    product = relationship('OlistProductsDataset', back_populates='order_items')
    seller = relationship('OlistSellersDataset', back_populates='order_items')

class OlistOrderPaymentsDataset(Base):
    __tablename__ = 'olist_order_payments_dataset'
    order_id = Column(String, ForeignKey('olist_orders_dataset.order_id'), primary_key=True)
    payment_sequential = Column(Integer, primary_key=True)
    payment_type = Column(String)
    payment_installments = Column(Integer)
    payment_value = Column(Float)
    # Relationships
    order = relationship('OlistOrdersDataset', back_populates='order_payments')

class OlistOrderReviewsDataset(Base):
    __tablename__ = 'olist_order_reviews_dataset'
    review_id = Column(String, primary_key=True)
    order_id = Column(String, ForeignKey('olist_orders_dataset.order_id'))
    review_score = Column(Integer)
    review_comment_title = Column(String)
    review_comment_message = Column(String)
    review_creation_date = Column(DateTime)
    review_answer_timestamp = Column(DateTime)
    # Relationships
    order = relationship('OlistOrdersDataset', back_populates='order_reviews')

class OlistProductsDataset(Base):
    __tablename__ = 'olist_products_dataset'
    product_id = Column(String, primary_key=True)
    product_category_name = Column(String)
    product_name_lenght = Column(Integer)
    product_description_lenght = Column(Integer)
    product_photos_qty = Column(Integer)
    product_weight_g = Column(Integer)
    product_length_cm = Column(Integer)
    product_height_cm = Column(Integer)
    product_width_cm = Column(Integer)
    # Relationships
    order_items = relationship('OlistOrderItemsDataset', back_populates='product')

class OlistSellersDataset(Base):
    __tablename__ = 'olist_sellers_dataset'
    seller_id = Column(String, primary_key=True)
    seller_zip_code_prefix = Column(Integer)
    seller_city = Column(String)
    seller_state = Column(String)
    # Relationships
    order_items = relationship('OlistOrderItemsDataset', back_populates='seller')

class OlistGeolocationDataset(Base):
    __tablename__ = 'olist_geolocation_dataset'
    geolocation_zip_code_prefix = Column(Integer, primary_key=True)
    geolocation_lat = Column(Float)
    geolocation_lng = Column(Float)
    geolocation_city = Column(String)
    geolocation_state = Column(String)

class ProductCategoryNameTranslation(Base):
    __tablename__ = 'product_category_name_translation'
    product_category_name = Column(String, primary_key=True)
    product_category_name_english = Column(String)