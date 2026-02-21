import mlflow

# 1. Connect to your local MLflow Database
mlflow.set_tracking_uri("sqlite:///mlflow.db")

print("🔍 Searching for the latest model...")

# 2. Find your experiment
experiment = mlflow.get_experiment_by_name("Titan_Insurance_Pricing")
runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])

# Get the ID of the very last run you did
latest_run_id = runs.loc[0, 'run_id']

# 3. Create the unique URI (path) to your model
model_uri = f"runs:/{latest_run_id}/model"

print(f"🚀 Registering Run ID: {latest_run_id}...")

# 4. Register it!
result = mlflow.register_model(model_uri, "Titan-Production-Model")

print(f"✅ Success! Registered 'Titan-Production-Model' as Version {result.version}.")