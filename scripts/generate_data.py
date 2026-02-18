import pandas as pd
import numpy as np
import os

# Settings
NUM_SAMPLES = 5000
# Ensure we save to the data folder relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(BASE_DIR, "../data/insurance_claims.csv")

def generate_insurance_data():
    print("🎲 Generating Synthetic Data...")
    np.random.seed(42)
    
    # 1. Generate Features
    age = np.random.randint(18, 65, size=NUM_SAMPLES)
    bmi = np.random.normal(30, 6, size=NUM_SAMPLES)
    smoker = np.random.choice(['yes', 'no'], size=NUM_SAMPLES, p=[0.2, 0.8])
    children = np.random.randint(0, 5, size=NUM_SAMPLES)
    
    # 2. Calculate Charges (y = mx + c + noise)
    charges = 2000 + (age * 250) + (bmi * 330) + (children * 500)
    charges += np.where(smoker == 'yes', 24000, 0)
    charges += np.random.normal(0, 1000, size=NUM_SAMPLES)
    
    # 3. Create DataFrame
    df = pd.DataFrame({
        'age': age,
        'bmi': bmi.round(2),
        'smoker': smoker,
        'children': children,
        'charges': charges.round(2)
    })
    
    # 4. Save
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Data saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_insurance_data()