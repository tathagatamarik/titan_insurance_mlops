import pandas as pd
import numpy as np
import joblib
import os
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score

def train():
    print("⏳ Loading Data...")
    base_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_path, '../data/insurance_claims.csv')
    
    df = pd.read_csv(data_path)
    X = df.drop('charges', axis=1)
    y = df['charges']

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), ['age', 'bmi', 'children']),
            ('cat', OneHotEncoder(), ['smoker'])
        ])

    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', LinearRegression())
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # --- MLFLOW TRACKING STARTS HERE ---
    print("🚂 Training Model with MLflow Tracking...")
    
    # Set up a local MLflow directory
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("Titan_Insurance_Pricing")

    with mlflow.start_run():
        # Train
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        
        # Calculate Metrics (Using numpy to avoid version conflicts)
        mse = mean_squared_error(y_test, predictions)
        rmse = np.sqrt(mse) 
        r2 = r2_score(y_test, predictions)
        
        # 1. Log Metrics
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2_score", r2)
        
        # 2. Log Parameters
        mlflow.log_param("test_size", 0.2)
        mlflow.log_param("model_type", "LinearRegression")
        
        # 3. Log the Model 
        mlflow.sklearn.log_model(model, "model")
        
        print(f"✅ Model Tracked! RMSE: ${rmse:.2f} | R2: {r2:.4f}")

        # Save local .pkl for Flask
        joblib.dump(model, os.path.join(base_path, 'insurance_model.pkl'))

if __name__ == "__main__":
    train()