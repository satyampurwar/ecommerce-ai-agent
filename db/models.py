"""SQLAlchemy ORM models for the Olist e-commerce dataset."""

from sqlalchemy.orm import declarative_base, relationship, foreign
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, SmallInteger

Base = declarative_base()

class OlistCustomersDataset(Base):
    """ORM model for the ``olist_customers_dataset`` table."""
    __tablename__ = "olist_customers_dataset"

    customer_id = Column(String(50), primary_key=True, nullable=False)
    customer_unique_id = Column(String(50), nullable=False)
    customer_zip_code_prefix = Column(Integer, nullable=False)
    customer_city = Column(String(50), nullable=False)
    customer_state = Column(String(50), nullable=False)

    # Relationships
    orders = relationship("OlistOrdersDataset", back_populates="customer")


class OlistOrdersDataset(Base):
    """ORM model for the ``olist_orders_dataset`` table."""
    __tablename__ = "olist_orders_dataset"

    order_id = Column(String(50), primary_key=True, nullable=False)
    customer_id = Column(
        String(50), ForeignKey("olist_customers_dataset.customer_id"), nullable=False
    )
    order_status = Column(String(50), nullable=False)
    order_purchase_timestamp = Column(DateTime, nullable=False)
    order_approved_at = Column(DateTime, nullable=True)
    order_delivered_carrier_date = Column(DateTime, nullable=True)
    order_delivered_customer_date = Column(DateTime, nullable=True)
    order_estimated_delivery_date = Column(DateTime, nullable=False)

    # Relationships
    customer = relationship("OlistCustomersDataset", back_populates="orders")
    order_items = relationship("OlistOrderItemsDataset", back_populates="order")
    order_payments = relationship("OlistOrderPaymentsDataset", back_populates="order")
    order_reviews = relationship("OlistOrderReviewsDataset", back_populates="order")


class OlistOrderItemsDataset(Base):
    """ORM model for line items belonging to an order."""
    __tablename__ = "olist_order_items_dataset"

    order_id = Column(
        String(50),
        ForeignKey("olist_orders_dataset.order_id"),
        primary_key=True,
        nullable=False,
    )
    order_item_id = Column(SmallInteger, primary_key=True, nullable=False)
    product_id = Column(
        String(50), ForeignKey("olist_products_dataset.product_id"), nullable=False
    )
    seller_id = Column(
        String(50), ForeignKey("olist_sellers_dataset.seller_id"), nullable=False
    )
    shipping_limit_date = Column(DateTime, nullable=False)
    price = Column(Float, nullable=False)
    freight_value = Column(Float, nullable=False)

    # Relationships
    order = relationship("OlistOrdersDataset", back_populates="order_items")
    product = relationship("OlistProductsDataset", back_populates="order_items")
    seller = relationship("OlistSellersDataset", back_populates="order_items")


class OlistOrderPaymentsDataset(Base):
    """ORM model capturing payment information for an order."""
    __tablename__ = "olist_order_payments_dataset"

    order_id = Column(
        String(50),
        ForeignKey("olist_orders_dataset.order_id"),
        primary_key=True,
        nullable=False,
    )
    payment_sequential = Column(SmallInteger, primary_key=True, nullable=False)
    payment_type = Column(String(50), nullable=False)
    payment_installments = Column(SmallInteger, nullable=False)
    payment_value = Column(Float, nullable=False)

    # Relationships
    order = relationship("OlistOrdersDataset", back_populates="order_payments")


class OlistOrderReviewsDataset(Base):
    """ORM model for customer reviews associated with an order."""
    __tablename__ = "olist_order_reviews_dataset"

    review_id = Column(String(50), primary_key=True, nullable=False)
    order_id = Column(
        String(50), ForeignKey("olist_orders_dataset.order_id"), nullable=False
    )
    review_score = Column(SmallInteger, nullable=False)
    review_comment_title = Column(String(50), nullable=True)
    review_comment_message = Column(String(250), nullable=True)
    review_creation_date = Column(DateTime, nullable=False)
    review_answer_timestamp = Column(DateTime, nullable=False)

    # Relationships
    order = relationship("OlistOrdersDataset", back_populates="order_reviews")


class OlistProductsDataset(Base):
    """ORM model describing individual products."""
    __tablename__ = "olist_products_dataset"

    product_id = Column(String(50), primary_key=True, nullable=False)
    product_category_name = Column(String(50), nullable=True)
    product_name_lenght = Column(Integer, nullable=True)
    product_description_lenght = Column(Integer, nullable=True)
    product_photos_qty = Column(SmallInteger, nullable=True)
    product_weight_g = Column(Integer, nullable=True)
    product_length_cm = Column(Integer, nullable=True)
    product_height_cm = Column(Integer, nullable=True)
    product_width_cm = Column(Integer, nullable=True)

    # Relationships
    order_items = relationship("OlistOrderItemsDataset", back_populates="product")
    category_translation = relationship(
        "ProductCategoryNameTranslation",
        primaryjoin="foreign(OlistProductsDataset.product_category_name) == ProductCategoryNameTranslation.product_category_name",
        back_populates="products",
        viewonly=True,
        uselist=False,
    )


class OlistSellersDataset(Base):
    """ORM model containing seller information."""
    __tablename__ = "olist_sellers_dataset"

    seller_id = Column(String(50), primary_key=True, nullable=False)
    seller_zip_code_prefix = Column(Integer, nullable=False)
    seller_city = Column(String(50), nullable=False)
    seller_state = Column(String(50), nullable=False)

    # Relationships
    order_items = relationship("OlistOrderItemsDataset", back_populates="seller")


class OlistGeolocationDataset(Base):
    """ORM model for geographic coordinates of zip codes."""
    __tablename__ = "olist_geolocation_dataset"

    geolocation_zip_code_prefix = Column(Integer, primary_key=True, nullable=False)
    geolocation_lat = Column(Float, nullable=False)
    geolocation_lng = Column(Float, nullable=False)
    geolocation_city = Column(String(50), nullable=False)
    geolocation_state = Column(String(50), nullable=False)


class ProductCategoryNameTranslation(Base):
    """ORM model mapping product category names to English."""
    __tablename__ = "product_category_name_translation"

    product_category_name = Column(String(50), primary_key=True, nullable=False)
    product_category_name_english = Column(String(50), nullable=False)

    # Relationships
    products = relationship(
        "OlistProductsDataset",
        primaryjoin="foreign(OlistProductsDataset.product_category_name) == ProductCategoryNameTranslation.product_category_name",
        back_populates="category_translation",
        viewonly=True,
    )
