# 🚀 End-to-End E-Commerce Data Pipeline

![Python](https://img.shields.io/badge/Python-3.8-blue)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-2.8.0-green)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![MongoDB](https://img.shields.io/badge/MongoDB-7.0-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-yellow)

## 📌 Project Overview
A production-style, end-to-end data engineering pipeline built from scratch using real Brazilian e-commerce data (100,000+ orders). Raw CSV data is ingested into MongoDB, transformed using Pandas, stored in PostgreSQL, orchestrated by Apache Airflow, and visualized in a Power BI dashboard — all containerized with Docker.

## 🏗️ Architecture

## 🛠️ Tech Stack
| Tool | Purpose |
|------|---------|
| Python | Data ingestion & transformation |
| Apache Airflow | Pipeline orchestration & scheduling |
| MongoDB | Raw data storage |
| PostgreSQL | Analytics data warehouse |
| Pandas | Data transformation |
| Docker | Containerization |
| Power BI | Business Intelligence dashboard |

## 📊 Dataset
- **Source:** Olist Brazilian E-Commerce (Kaggle)
- **Size:** 100,000+ real orders
- **Files:** 8 CSV files (orders, items, products, customers, reviews, payments, sellers, categories)

## 🔄 Pipeline Tasks
1. **ingest_to_mongodb** — Loads 8 CSV files into MongoDB collections
2. **validate_mongodb** — Validates data was loaded correctly
3. **spark_transform** — Cleans and transforms data, writes to PostgreSQL
4. **validate_postgresql** — Confirms analytics tables are populated

## 📈 Analytics Tables Built
- **daily_revenue** — Revenue and orders per day (616 rows)
- **top_products** — Top 20 product categories by revenue
- **customer_metrics** — Customer distribution by Brazilian state

## 🚀 How to Run
1. Clone this repository
2. Download Olist dataset from Kaggle and place CSV files in `/data` folder
3. Run `docker-compose up -d`
4. Copy DAG file: `docker cp airflow/dags/pipeline_dag.py ecommerce-pipeline-airflow-scheduler-1:/opt/airflow/dags/`
5. Open Airflow at `http://localhost:8085` (admin/admin123)
6. Trigger the `ecommerce_pipeline` DAG
7. Connect Power BI to PostgreSQL or use exported CSV files

## 📁 Project Structure

## 💼 Key Achievements
- Processed **99,441 real e-commerce orders** end-to-end
- Reduced reporting time from **hours to minutes** via automation
- Built **fully containerized** pipeline running on any machine
- Implemented **data validation** at every pipeline stage
- Created **interactive Power BI dashboard** with 4 visualizations

## 👨‍💻 Developer
**Ayush Dewli** — BCA Student, Galgotias University
- Aspiring Data Analyst / Data Engineer