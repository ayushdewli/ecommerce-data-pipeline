CREATE USER pipeline WITH PASSWORD 'pipeline';
CREATE DATABASE ecommerce OWNER pipeline;

\c ecommerce

CREATE TABLE IF NOT EXISTS daily_revenue (
    order_date      DATE PRIMARY KEY,
    total_revenue   NUMERIC(12,2),
    total_orders    INT,
    avg_order_value NUMERIC(10,2)
);

CREATE TABLE IF NOT EXISTS top_products (
    product_category VARCHAR(100),
    total_sold       INT,
    total_revenue    NUMERIC(12,2),
    snapshot_date    DATE
);

CREATE TABLE IF NOT EXISTS customer_metrics (
    state            VARCHAR(10),
    total_customers  INT,
    avg_review_score NUMERIC(4,2),
    snapshot_date    DATE
);

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO pipeline;