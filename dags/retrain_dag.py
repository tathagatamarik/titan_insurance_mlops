from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess

# 1. Define the DAG Settings
default_args = {
    'owner': 'titan_mlops',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 2. Instantiate the DAG
dag = DAG(
    'drift_retraining_pipeline',
    default_args=default_args,
    description='Retrains the Titan ML model when data drift is detected',
    schedule_interval=None, # This means it waits for a Webhook trigger from Grafana!
    catchup=False
)

# 3. Define the Python Functions that Airflow will run
def download_fresh_data():
    print("📥 Downloading latest insurance claims from database...")
    # Code to query database goes here

def run_mlflow_training():
    print("🚂 Running src/train.py...")
    # Trigger the MLflow training script we built earlier
    subprocess.run(["python", "src/train.py"])

def deploy_to_kubernetes():
    print("🚀 Triggering GitHub Actions to deploy the new model to Azure AKS...")
    # Code to ping GitHub API goes here

# 4. Map Functions to Airflow Tasks using PythonOperator
task_download_data = PythonOperator(
    task_id='download_fresh_data',
    python_callable=download_fresh_data,
    dag=dag,
)

task_train_model = PythonOperator(
    task_id='train_model_with_mlflow',
    python_callable=run_mlflow_training,
    dag=dag,
)

task_deploy = PythonOperator(
    task_id='deploy_new_model',
    python_callable=deploy_to_kubernetes,
    dag=dag,
)

# 5. Define the Execution Order
task_download_data >> task_train_model >> task_deploy