from flask import Flask, request, jsonify
import joblib
import pandas as pd
import os

app = Flask(__name__)

# Load Model
base_path = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_path, 'insurance_model.pkl')
model = joblib.load(model_path)

@app.route('/')
def home():
    return "🚀 Titan Insurance API is Running!"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        # Convert JSON to DataFrame
        df = pd.DataFrame(data)
        
        # Predict
        prediction = model.predict(df)
        
        return jsonify({
            'prediction': prediction.tolist(),
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'})

if __name__ == '__main__':
    # Run on 0.0.0.0 so Docker can expose it
    app.run(host='0.0.0.0', port=5000)