from sqlalchemy.orm import Session
from db.models import (
    OlistOrdersDataset,
    OlistOrderPaymentsDataset,
    OlistOrderReviewsDataset,
)
from vectorstore.faq_vectorstore import semantic_faq_search
import re

# --- FAQ Tool ---

def search_faq(query, k=2):
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

# --- Tool Registry ---

tools = [
    faq_tool,
    order_status_tool,
    refund_status_tool,
    review_tool
]