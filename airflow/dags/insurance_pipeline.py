from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys
import os

# Add the src folder to the path so we can import our scripts
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

# Define the DAG (The Workflow)
default_args = {
    'owner': 'titan_user',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'titan_insurance_training_pipeline',
    default_args=default_args,
    description='A simple ML pipeline for Titan Insurance',
    schedule_interval=timedelta(days=1), # Run once every day
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    # Task 1: Print a welcome message
    start_task = BashOperator(
        task_id='start_pipeline',
        bash_command='echo "🚀 Starting Titan Insurance Pipeline..."'
    )

    # Task 2: Generate new data (Simulating new claims coming in)
    generate_data_task = BashOperator(
        task_id='generate_data',
        bash_command='python scripts/generate_data.py'
    )

    # Task 3: Retrain the Model
    # We use BashOperator here to run the script inside the container/environment
    train_model_task = BashOperator(
        task_id='train_model',
        bash_command='python src/train.py'
    )

    # Task 4: Notify Success
    end_task = BashOperator(
        task_id='end_pipeline',
        bash_command='echo "✅ Pipeline Finished Successfully!"'
    )

    # Define the order of tasks
    start_task >> generate_data_task >> train_model_task >> end_task