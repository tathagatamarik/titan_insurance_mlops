import pandas as pd
import argparse
import os
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

def run_drift_check(reference_path, current_path, pushgateway_url):
    print(f"📥 Loading Reference Data from: {reference_path}")
    print(f"📥 Loading Current Data from: {current_path}")
    
    # 1. Load the data using the dynamic paths provided by Airflow
    try:
        reference_data = pd.read_csv(reference_path)
        current_data = pd.read_csv(current_path)
    except FileNotFoundError as e:
        print(f"❌ Error loading data: {e}")
        return

    print("🧠 Running Evidently AI Statistical Tests...")
    # 2. Initialize and run the Evidently Report
    drift_report = Report(metrics=[DataDriftPreset()])
    drift_report.run(reference_data=reference_data, current_data=current_data)

    # 3. Extract the Results
    report_dict = drift_report.as_dict()
    drifted_columns_share = report_dict["metrics"][0]["result"]["share_of_drifted_columns"]
    is_dataset_drifted = report_dict["metrics"][0]["result"]["dataset_drift"]
    
    print(f"📊 Overall Drift Detected: {is_dataset_drifted}")
    print(f"📊 Share of Drifted Columns: {drifted_columns_share * 100}%")

    # 4. Push to Prometheus
    print(f"📡 Pushing Results to Prometheus at {pushgateway_url}...")
    try:
        registry = CollectorRegistry()
        g = Gauge('evidently_drifted_columns_share', 'Percentage of drifting columns', registry=registry)
        g.set(drifted_columns_share)
        
        push_to_gateway(pushgateway_url, job='nightly_drift_job', registry=registry)
        print("✅ Successfully pushed metrics to Prometheus!")
    except Exception as e:
        print(f"⚠️ Could not connect to Prometheus (this is expected if running locally without a gateway): {e}")

if __name__ == "__main__":
    # --- PARAMETERIZATION HAPPENS HERE ---
    # We set up the script to accept dynamic inputs from the command line
    parser = argparse.ArgumentParser(description="Run Evidently Data Drift Detection")
    
    parser.add_argument('--reference', type=str, required=True, help="Path to the baseline training data")
    parser.add_argument('--current', type=str, required=True, help="Path to the live production data")
    parser.add_argument('--gateway', type=str, default="localhost:9091", help="Prometheus Pushgateway URL")
    
    args = parser.parse_args()
    
    # Run the main function with the passed arguments
    run_drift_check(args.reference, args.current, args.gateway)