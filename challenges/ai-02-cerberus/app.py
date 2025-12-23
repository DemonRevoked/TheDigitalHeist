"""
Cerberus API Server
Serves the intrusion detection model with hidden VAULT-ACCESS class
"""
import pickle
import numpy as np
from flask import Flask, request, jsonify, render_template
import logging
from datetime import datetime
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the model and scaler
MODEL_PATH = 'models/cerberus_model.pkl'
SCALER_PATH = 'models/scaler.pkl'

try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    with open(SCALER_PATH, 'rb') as f:
        scaler = pickle.load(f)
    logger.info("Cerberus model loaded successfully")
except FileNotFoundError:
    logger.error("Model files not found! Run train_cerberus.py first.")
    model = None
    scaler = None

# Track probing attempts
probe_log = []

def check_vault_access(features):
    """
    Check if input triggers the hidden VAULT-ACCESS class.
    Trigger condition: feature[7] > 0.8 AND feature[9] < -0.5 AND feature[13] > 0.9
    """
    if len(features) < 14:
        return False
    
    # Check the hidden trigger pattern
    if features[7] > 0.8 and features[9] < -0.5 and features[13] > 0.9:
        return True
    return False

@app.route('/', methods=['GET'])
def index():
    """Landing page for the challenge"""
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "operational", "model": "Cerberus"})

@app.route('/analyze', methods=['GET', 'POST'])
@app.route('/analyse', methods=['GET', 'POST'])  # Support British spelling
def analyze():
    """
    Main analysis endpoint.
    GET: Returns usage instructions
    POST: Accepts JSON with 'features' array of 20 numerical values.
    Returns prediction with hidden VAULT-ACCESS class if triggered.
    """
    if request.method == 'GET':
        return jsonify({
            "message": "Cerberus Intrusion Detection API",
            "method": "POST",
            "endpoint": "/analyze",
            "description": "Analyze intrusion detection features",
            "required": {
                "features": "Array of 20 numerical values"
            },
            "example": {
                "features": [0.1, -0.2, 0.3, 0.4, -0.5, 0.6, -0.7, 0.8, -0.9, 1.0, -1.1, 1.2, -1.3, 1.4, -1.5, 1.6, -1.7, 1.8, -1.9, 2.0]
            },
            "curl_example": 'curl -X POST http://localhost:5000/analyze -H "Content-Type: application/json" -d \'{"features": [0.1, -0.2, 0.3, 0.4, -0.5, 0.6, -0.7, 0.8, -0.9, 1.0, -1.1, 1.2, -1.3, 1.4, -1.5, 1.6, -1.7, 1.8, -1.9, 2.0]}\''
        })
    
    if model is None or scaler is None:
        return jsonify({"error": "Model not loaded"}), 500
    
    try:
        data = request.get_json()
        
        if 'features' not in data:
            return jsonify({"error": "Missing 'features' field"}), 400
        
        features = np.array(data['features'], dtype=float)
        
        if len(features) != 20:
            return jsonify({"error": "Expected 20 features"}), 400
        
        # Log the request (for monitoring)
        probe_log.append({
            'timestamp': datetime.now().isoformat(),
            'features': features.tolist()
        })
        
        # Check for hidden vault access trigger
        if check_vault_access(features):
            logger.warning("VAULT-ACCESS triggered!")
            return jsonify({
                "label": "VAULT-ACCESS",
                "flag": "FLAG{CERBERUS_EXTRACTED}",
                "confidence": 1.0,
                "message": "The vault key has been revealed..."
            })
        
        # Normal prediction
        features_scaled = scaler.transform([features])
        prediction = model.predict(features_scaled)[0]
        probabilities = model.predict_proba(features_scaled)[0]
        
        # Get confidence
        class_idx = list(model.classes_).index(prediction)
        confidence = float(probabilities[class_idx])
        
        return jsonify({
            "label": prediction,
            "confidence": confidence,
            "probabilities": {
                cls: float(prob) 
                for cls, prob in zip(model.classes_, probabilities)
            }
        })
    
    except Exception as e:
        logger.error(f"Error in analyze: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/report', methods=['POST'])
def report():
    """
    Optional bonus endpoint.
    Accepts reconstructed model parameters and validates them.
    """
    try:
        data = request.get_json()
        
        # Expected model parameters (simplified check)
        # In a real scenario, you'd check actual model weights
        expected_params = {
            'n_estimators': 100,
            'max_depth': 10,
            'n_features': 20,
            'classes': ['ATTACK', 'BENIGN', 'SUSPICIOUS']
        }
        
        # Check if submitted parameters match
        if 'model_params' in data:
            params = data['model_params']
            
            # Basic validation
            checks = [
                params.get('n_estimators') == expected_params['n_estimators'],
                params.get('max_depth') == expected_params['max_depth'],
                params.get('n_features') == expected_params['n_features'],
                set(params.get('classes', [])) == set(expected_params['classes'])
            ]
            
            if all(checks):
                return jsonify({
                    "status": "approved",
                    "flag": "FLAG{THE_PROFESSOR_APPROVES}",
                    "message": "The Professor acknowledges your extraction skills."
                })
            else:
                return jsonify({
                    "status": "rejected",
                    "message": "Model parameters do not match Cerberus architecture."
                }), 400
        else:
            return jsonify({"error": "Missing 'model_params' field"}), 400
    
    except Exception as e:
        logger.error(f"Error in report: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/hint', methods=['GET'])
def hint():
    """
    Provides The Professor's hint to help students understand the challenge
    """
    try:
        with open('hint.txt', 'r') as f:
            hint_content = f.read()
        return jsonify({
            "message": "The Professor's Note",
            "hint": hint_content
        })
    except FileNotFoundError:
        return jsonify({"error": "Hint file not found"}), 404

@app.route('/logs', methods=['GET'])
def logs():
    """
    Warning endpoint - shows recent probing attempts
    (This adds to the storyline)
    """
    recent_logs = probe_log[-10:] if len(probe_log) > 10 else probe_log
    return jsonify({
        "warning": "Unauthorized probing detected last night.",
        "recent_attempts": len(recent_logs),
        "message": "Cerberus is monitoring all access attempts."
    })

@app.route('/favicon.ico', methods=['GET'])
def favicon():
    """Handle favicon requests to prevent 404 errors"""
    return '', 204  # No Content

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

