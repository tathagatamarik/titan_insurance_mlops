import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error

def train():
    print("⏳ Loading Data...")
    # Dynamic paths to work inside Docker and locally
    base_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_path, '../data/insurance_claims.csv')
    model_path = os.path.join(base_path, 'insurance_model.pkl')

    if not os.path.exists(data_path):
        print(f"❌ Error: Data not found at {data_path}")
        return

    df = pd.read_csv(data_path)
    X = df.drop('charges', axis=1)
    y = df['charges']

    # 1. Define Preprocessing
    # Scale numbers, One-Hot Encode text ('yes'/'no')
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), ['age', 'bmi', 'children']),
            ('cat', OneHotEncoder(), ['smoker'])
        ])

    # 2. Create Pipeline
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', LinearRegression())
    ])

    # 3. Train
    print("🚂 Training Model...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)

    # 4. Evaluate
    predictions = model.predict(X_test)
    rmse = mean_squared_error(y_test, predictions, squared=False)
    print(f"✅ Model Trained! RMSE: ${rmse:.2f}")

    # 5. Save
    joblib.dump(model, model_path)
    print(f"💾 Model saved to {model_path}")

if __name__ == "__main__":
    train()