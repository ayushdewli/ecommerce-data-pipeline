import pandas as pd
from pymongo import MongoClient
import psycopg2
from psycopg2.extras import execute_values
from datetime import date

def get_mongo_data():
    client = MongoClient('mongodb://mongo:27017/')
    db = client['olist_raw']
    
    orders = pd.DataFrame(list(db.orders.find({}, {'_id': 0})))
    order_items = pd.DataFrame(list(db.order_items.find({}, {'_id': 0})))
    products = pd.DataFrame(list(db.products.find({}, {'_id': 0})))
    customers = pd.DataFrame(list(db.customers.find({}, {'_id': 0})))
    reviews = pd.DataFrame(list(db.reviews.find({}, {'_id': 0})))
    
    print(f"Orders loaded: {len(orders)}")
    print(f"Order items loaded: {len(order_items)}")
    
    client.close()
    return orders, order_items, products, customers, reviews

def get_pg_connection():
    return psycopg2.connect(
        host='postgres',
        dbname='ecommerce',
        user='pipeline',
        password='pipeline'
    )

def build_daily_revenue(orders, order_items):
    print("Building daily_revenue...")
    
    orders['order_purchase_timestamp'] = pd.to_datetime(
        orders['order_purchase_timestamp'], errors='coerce'
    )
    orders['order_date'] = orders['order_purchase_timestamp'].dt.date
    
    merged = order_items.merge(orders[['order_id', 'order_date']], on='order_id', how='left')
    
    daily = merged.groupby('order_date').agg(
        total_revenue=('price', 'sum'),
        total_orders=('order_id', 'nunique')
    ).reset_index()
    
    daily = daily.dropna(subset=['order_date'])
    daily['avg_order_value'] = (daily['total_revenue'] / daily['total_orders']).round(2)
    daily['total_revenue'] = daily['total_revenue'].round(2)
    daily['total_orders'] = daily['total_orders'].astype(int)
    print(f"Daily revenue rows: {len(daily)}")
    return daily[['order_date', 'total_revenue', 'total_orders', 'avg_order_value']]

def build_top_products(order_items, products):
    print("Building top_products...")
    
    merged = order_items.merge(
        products[['product_id', 'product_category_name']], 
        on='product_id', how='left'
    )
    
    top = merged.groupby('product_category_name').agg(
        total_sold=('order_id', 'count'),
        total_revenue=('price', 'sum')
    ).reset_index()
    
    top = top.dropna(subset=['product_category_name'])
    top = top.sort_values('total_revenue', ascending=False).head(20)
    top = top.rename(columns={'product_category_name': 'product_category'})
    top['total_revenue'] = top['total_revenue'].round(2)
    top['snapshot_date'] = date.today()
    print(f"Top products rows: {len(top)}")
    return top[['product_category', 'total_sold', 'total_revenue', 'snapshot_date']]

def build_customer_metrics(orders, customers, reviews):
    print("Building customer_metrics...")
    
    merged = orders.merge(
        customers[['customer_id', 'customer_state']], 
        on='customer_id', how='left'
    )
    
    # Get avg review score per state
    order_reviews = merged.merge(
        reviews[['order_id', 'review_score']], 
        on='order_id', how='left'
    )
    
    metrics = order_reviews.groupby('customer_state').agg(
        total_customers=('customer_id', 'nunique'),
        avg_review_score=('review_score', 'mean')
    ).reset_index()
    
    metrics = metrics.dropna(subset=['customer_state'])
    metrics = metrics.rename(columns={'customer_state': 'state'})
    metrics['avg_review_score'] = metrics['avg_review_score'].round(2)
    metrics['snapshot_date'] = date.today()
    print(f"Customer metrics rows: {len(metrics)}")
    return metrics[['state', 'total_customers', 'avg_review_score', 'snapshot_date']]

def write_to_postgres(df, table_name, conn):
    print(f"Writing {table_name} to PostgreSQL...")
    cur = conn.cursor()
    cur.execute(f"TRUNCATE TABLE {table_name}")
    
    cols = list(df.columns)
    values = [tuple(row) for row in df.itertuples(index=False)]
    
    insert_sql = f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES %s"
    execute_values(cur, insert_sql, values)
    conn.commit()
    cur.close()
    print(f"✅ {table_name} written successfully — {len(df)} rows")

def run():
    print("=== Starting Transform ===")
    orders, order_items, products, customers, reviews = get_mongo_data()
    
    conn = get_pg_connection()
    
    daily_revenue = build_daily_revenue(orders, order_items)
    write_to_postgres(daily_revenue, 'daily_revenue', conn)
    
    top_products = build_top_products(order_items, products)
    write_to_postgres(top_products, 'top_products', conn)
    
    customer_metrics = build_customer_metrics(orders, customers, reviews)
    write_to_postgres(customer_metrics, 'customer_metrics', conn)
    
    conn.close()
    print("=== Transform Complete ===")

if __name__ == '__main__':
    run()