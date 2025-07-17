+-----------------------------+
|  olist_customers_dataset    |
+-----------------------------+
| customer_id (PK)            |
| customer_unique_id          |
| customer_zip_code_prefix    |
| customer_city               |
| customer_state              |
+-----------------------------+
             |
             | FK
             v
+-----------------------------+
|   olist_orders_dataset      |
+-----------------------------+
| order_id (PK)               |
| customer_id (FK)            |
| order_status                |
| order_purchase_timestamp    |
| order_approved_at           |
| order_delivered_carrier_date|
| order_delivered_customer_date|
| order_estimated_delivery_date|
+-----------------------------+
   |       |         |
   |       |         |
   |       |         |
   |       |         |
   |       |         +-------------------------------+
   |       |                                       |
   |       |                                       v
   |       +-------------------------------+   +--------------------------+
   |                                       |   | olist_order_reviews_ds   |
   |                                       |   +--------------------------+
   |                                       |   | review_id                |
   |                                       |   | order_id (FK)            |
   |                                       |   | review_score             |
   |                                       |   | review_comment_title     |
   |                                       |   | review_comment_message   |
   |                                       |   | review_creation_date     |
   |                                       |   | review_answer_timestamp  |
   |                                       |   +--------------------------+
   |                                       |
   |                                       +--------------------------+
   |                                                                  |
   v                                                                  v
+-------------------------------+       +--------------------------+
| olist_order_items_dataset     |       | olist_order_payments_ds  |
+-------------------------------+       +--------------------------+
| order_id (FK)                 |       | order_id (FK)            |
| order_item_id                 |       | payment_sequential       |
| product_id (FK)               |       | payment_type             |
| seller_id (FK)                |       | payment_installments     |
| shipping_limit_date           |       | payment_value            |
| price                         |       +--------------------------+
| freight_value                 |
+-------------------------------+
   |              |
   |              |
   v              v
+----------------------+    +----------------------+
| olist_products_ds    |    | olist_sellers_ds     |
+----------------------+    +----------------------+
| product_id (PK)      |    | seller_id (PK)       |
| product_category_name|    | seller_zip_code_prefix|
| product_name_lenght  |    | seller_city          |
| ...                  |    | seller_state         |
+----------------------+    +----------------------+

+-------------------------------+
| olist_geolocation_dataset     |  (no direct FK constraints)
+-------------------------------+
| geolocation_zip_code_prefix   |
| geolocation_lat               |
| geolocation_lng               |
| geolocation_city              |
| geolocation_state             |
+-------------------------------+
