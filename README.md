# 🏥 Titan Insurance AI: Enterprise MLOps Pipeline

## 📌 Project Overview
Titan Insurance AI is a fully automated, production-grade Machine Learning pipeline that predicts medical insurance costs based on patient demographics. 

This project goes beyond a simple Jupyter Notebook by implementing a complete **MLOps lifecycle** including Model Tracking, Real-time Feature Serving, Data Drift Detection, and Automated Retraining Orchestration.

## 🛠️ Tech Stack & Architecture
* **Model Tracking:** MLflow (SQLite Backend)
* **Live API & Web App:** Flask / Python
* **Feature Store:** Feast (Offline: Parquet | Online: Redis)
* **Data Drift Monitoring:** Evidently AI
* **Time-Series Database:** Prometheus
* **Observability & Alerting:** Grafana (Provisioned via Docker)
* **Orchestration:** Apache Airflow

## 🔄 The System Flow
1. **Feature Engineering:** Feast calculates and stores patient statistics (Age, BMI, Smoker status) in an offline Parquet file for training, and pushes the freshest data to a low-latency **Redis** online store.
2. **Training & Registry:** `train.py` pulls historical features from Feast, trains a regression model, and logs the artifacts and metrics directly into the **MLflow Vault**.
3. **Live Serving:** When a user accesses the Flask UI, the API instantly fetches their latest stats from the Redis Online Store and passes them to the MLflow model for a real-time prediction.
4. **Drift Detection:** The Flask app intercepts live traffic and broadcasts mathematical data drift scores (calculated via **Evidently AI** logic) to a `/metrics` endpoint.
5. **Observability:** **Prometheus** scrapes the drift metrics every 10 seconds. **Grafana** visualizes this data on a live dashboard.
6. **Automated Healing:** If Grafana detects a Data Drift score > 0.50, it fires a Webhook to **Apache Airflow**. Airflow triggers a DAG (`retrain_dag.py`) that automatically pulls fresh data, retrains a new model in MLflow, and heals the pipeline.

## 🚀 How to Run Locally

**1. Start the Infrastructure (Prometheus, Grafana, Redis)**
```bash
docker-compose up -d