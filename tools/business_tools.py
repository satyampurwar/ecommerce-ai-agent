from sqlalchemy.orm import Session
from db.models import (
    OlistOrdersDataset,
    OlistOrderPaymentsDataset,
    OlistOrderReviewsDataset,
    OlistCustomersDataset,
    OlistOrderItemsDataset,
    OlistProductsDataset,
    OlistSellersDataset,
    ProductCategoryNameTranslation,
)
from vectorstore.faq_vectorstore import semantic_faq_search
import re

# --- FAQ Tool ---

def search_faq(query, k=1):
    """
    Semantic FAQ search using vectorstore.
    """
    return semantic_faq_search(query, k=k)

faq_tool = {
    "name": "faq_search",
    "func": search_faq,
    "description": "Semantic search in FAQ for general questions."
}

# --- Order Status Tool ---

def get_order_status(query, session: Session):
    """
    Retrieve order status from DB using order_id found in the query.
    """
    match = re.search(r'(\b[0-9a-f]{32,}\b)', query)
    order_id = match.group(1) if match else None
    if not order_id:
        return "Please provide a valid order ID (32-character hex)."
    order = session.query(OlistOrdersDataset).filter_by(order_id=order_id).first()
    if not order:
        return f"No order found for ID: {order_id}."
    return (
        f"Order {order_id} status: {order.order_status}\n"
        f"Purchased: {order.order_purchase_timestamp}\n"
        f"Estimated delivery: {order.order_estimated_delivery_date}"
    )

order_status_tool = {
    "name": "order_status_lookup",
    "func": get_order_status,
    "description": "Look up order status by order_id. Pass SQLAlchemy session as the second argument."
}

# --- Refund Status Tool ---

def get_refund_status(query, session: Session):
    """
    Check refund/payment info for an order.
    """
    match = re.search(r'(\b[0-9a-f]{32,}\b)', query)
    order_id = match.group(1) if match else None
    if not order_id:
        return "Please provide a valid order ID (32-character hex)."
    payments = session.query(OlistOrderPaymentsDataset).filter_by(order_id=order_id).all()
    if not payments:
        return f"No payment info for order {order_id}."
    total_paid = sum(p.payment_value or 0 for p in payments)
    if total_paid == 0:
        return f"Order {order_id} was fully refunded."
    return f"Order {order_id} was paid {total_paid:.2f}, refund status unknown."

refund_status_tool = {
    "name": "refund_status_lookup",
    "func": get_refund_status,
    "description": "Check if an order has been refunded by order_id. Pass SQLAlchemy session as the second argument."
}

# --- Review Tool ---

def get_review(query, session: Session):
    """
    Retrieve review score/message for an order.
    """
    match = re.search(r'(\b[0-9a-f]{32,}\b)', query)
    order_id = match.group(1) if match else None
    if not order_id:
        return "Please provide a valid order ID (32-character hex)."
    review = session.query(OlistOrderReviewsDataset).filter_by(order_id=order_id).first()
    if not review:
        return f"No review found for order {order_id}."
    msg = review.review_comment_message or 'No comment.'
    return f"Review for order {order_id}:\nScore: {review.review_score}\nMessage: {msg}"

review_tool = {
    "name": "review_lookup",
    "func": get_review,
    "description": "Retrieve review and score for an order by order_id. Pass SQLAlchemy session as the second argument."
}

# --- Comprehensive Order Details Tool ---

def get_order_details(query, session: Session):
    """
    Retrieve a detailed summary for an order including customer, items,
    payments and reviews.
    """
    match = re.search(r'(\b[0-9a-f]{32,}\b)', query)
    order_id = match.group(1) if match else None
    if not order_id:
        return "Please provide a valid order ID (32-character hex)."
    order = session.query(OlistOrdersDataset).filter_by(order_id=order_id).first()
    if not order:
        return f"No order found for ID: {order_id}."

    customer = order.customer
    lines = [
        f"Order {order.order_id} status: {order.order_status}",
        f"Purchased: {order.order_purchase_timestamp}",
        f"Estimated delivery: {order.order_estimated_delivery_date}",
    ]
    if customer:
        lines.append(
            f"Customer {customer.customer_unique_id} in {customer.customer_city}, {customer.customer_state}"
        )

    if order.order_items:
        lines.append("Items:")
        for item in order.order_items:
            product = item.product
            seller = item.seller
            cat = None
            if product and product.category_translation:
                cat = product.category_translation.product_category_name_english
            elif product:
                cat = product.product_category_name
            lines.append(
                f"  - {item.product_id} ({cat or 'unknown category'}) from {seller.seller_id} price {item.price:.2f}"
            )
    if order.order_payments:
        total = sum(p.payment_value or 0 for p in order.order_payments)
        methods = ", ".join({p.payment_type for p in order.order_payments})
        lines.append(f"Payments: {total:.2f} via {methods}")
    if order.order_reviews:
        r = order.order_reviews[0]
        msg = r.review_comment_message or 'No comment.'
        lines.append(f"Review: {r.review_score} - {msg}")

    return "\n".join(lines)

order_details_tool = {
    "name": "order_details_lookup",
    "func": get_order_details,
    "description": "Retrieve comprehensive details for an order. Pass SQLAlchemy session as the second argument."
}

# --- Tool Registry ---

tools = [
    faq_tool,
    order_status_tool,
    refund_status_tool,
    review_tool,
    order_details_tool
]