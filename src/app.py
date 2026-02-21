from flask import Flask, request, jsonify, render_template_string
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST
import joblib
import pandas as pd
import os

app = Flask(__name__)

# --- 1. Load the AI Brain ---
base_path = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_path, 'insurance_model.pkl')
model = joblib.load(model_path)

# --- 2. Initialize Prometheus Metrics ---
# A "Gauge" is a metric dial that can go up and down (perfect for drift scores)
drift_score_gauge = Gauge('model_data_drift_score', 'Data drift score calculated by Evidently')

# --- 3. Define the User Interface (HTML) ---
HTML_INTERFACE = """
<!DOCTYPE html>
<html>
<head>
    <title>Titan Insurance AI</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .container { background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); width: 350px; }
        h1 { color: #333; text-align: center; font-size: 24px; }
        label { display: block; margin-top: 15px; color: #666; }
        input, select { width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        button { background-color: #007bff; color: white; border: none; padding: 12px; width: 100%; margin-top: 20px; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background-color: #0056b3; }
        .result { margin-top: 20px; padding: 15px; background-color: #e9ecef; border-left: 5px solid #007bff; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏥 Titan Insurance AI</h1>
        <form action="/predict_ui" method="post">
            <label>Age</label>
            <input type="number" name="age" required value="30">
            
            <label>BMI (Body Mass Index)</label>
            <input type="number" step="0.1" name="bmi" required value="25.0">
            
            <label>Children</label>
            <input type="number" name="children" required value="0">
            
            <label>Smoker?</label>
            <select name="smoker">
                <option value="no">No</option>
                <option value="yes">Yes</option>
            </select>
            
            <button type="submit">Predict Cost 💰</button>
        </form>
        
        {% if prediction %}
        <div class="result">
            <strong>Estimated Cost:</strong><br>
            <span style="font-size: 20px; color: #28a745;">${{ prediction }}</span>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

# --- 4. Web Routes ---

@app.route('/')
def home():
    # Serve the visual HTML form
    return render_template_string(HTML_INTERFACE)

@app.route('/predict_ui', methods=['POST'])
def predict_ui():
    # Handle human submissions from the browser
    try:
        age = int(request.form['age'])
        bmi = float(request.form['bmi'])
        children = int(request.form['children'])
        smoker = request.form['smoker']
        
        data = pd.DataFrame([[age, bmi, children, smoker]], columns=['age', 'bmi', 'children', 'smoker'])
        prediction = model.predict(data)[0]
        
        # 🚨 MLOps: Calculate & Broadcast Drift!
        # Mock logic: If a smoker applies, we pretend data drifted and spike the score to 0.85
        current_drift_score = 0.85 if smoker == 'yes' else 0.05
        drift_score_gauge.set(current_drift_score)
        
        return render_template_string(HTML_INTERFACE, prediction=round(prediction, 2))
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/predict', methods=['POST'])
def predict_api():
    # Handle robotic JSON submissions (for the testing script)
    try:
        data = request.json
        df = pd.DataFrame(data)
        prediction = model.predict(df)
        
        # 🚨 MLOps: Calculate & Broadcast Drift!
        is_smoker = str(df['smoker'].iloc[0]).lower()
        current_drift_score = 0.85 if is_smoker == 'yes' else 0.05
        drift_score_gauge.set(current_drift_score)
        
        return jsonify({'prediction': prediction.tolist(), 'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'})

# --- 5. The MLOps Scrape Endpoint ---
@app.route('/metrics')
def metrics():
    # Prometheus visits this URL every 10 seconds to read the gauges
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)