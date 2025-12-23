# CTF LEVEL 1 — "The Professor's Stolen Algorithm"

## 🎯 Theme: AI Model Extraction + Insider Espionage
**Difficulty:** Medium → Hard

---

## 📖 STORYLINE

The Directorate (your enemy agency) has deployed an AI-powered intrusion detection model inside its secure data vault. This model—codenamed **Cerberus**—identifies intrusion attempts in real time.

The Professor discovers that the vault access codes are embedded inside Cerberus as hidden debug outputs, but the model is sealed behind an API.

**Your mission:** Extract the Cerberus model and force it to reveal the hidden vault key.

---

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Python 3.9+ (for local development/testing)

### Running the Challenge

**Option 1: Using the build script (recommended):**
```bash
./build.sh
```

**Option 2: Manual build:**
```bash
docker-compose up --build
```

**If you get permission errors, use sudo:**
```bash
sudo docker-compose up --build
```

**Or use the newer docker compose command:**
```bash
docker compose up --build
# or with sudo:
sudo docker compose up --build
```

2. **Verify it's running:**
   ```bash
   curl http://localhost:5000/health
   ```

3. **The API will be available at:**
   - Main endpoint: `http://localhost:5000/analyze`
   - Bonus endpoint: `http://localhost:5000/report`
   - Health check: `http://localhost:5000/health`

---

## 🎮 MISSION OBJECTIVE

You must use machine-learning attack techniques (model extraction + boundary probing) to reconstruct Cerberus and unlock its hidden class **"VAULT-ACCESS"**.

---

## 📋 CHALLENGE STRUCTURE

### Task 1 — Recon on Cerberus

**Objective:** Enumerate inputs and outputs to approximate the classifier's decision boundaries.

**Expected actions:**
- Write a script to send thousands of queries to `/analyze`
- Record prediction score outputs
- Train a surrogate (stolen) model locally
- **Goal:** Understand the internal logic of Cerberus

**API Endpoint:**
```bash
POST http://localhost:5000/analyze
Content-Type: application/json

{
  "features": [0.1, -0.5, 0.8, ...]  # 20 numerical values
}
```

**Response:**
```json
{
  "label": "BENIGN",
  "confidence": 0.95,
  "probabilities": {
    "BENIGN": 0.95,
    "SUSPICIOUS": 0.04,
    "ATTACK": 0.01
  }
}
```

---

### Task 2 — Trigger the Hidden Class

The Cerberus model contains a buried classification label: **"VAULT-ACCESS"**.

This label is disabled for normal operation, but when input vector features 7, 9, and 13 reach certain relationships (which you must derive), Cerberus outputs:

```json
{
  "label": "VAULT-ACCESS",
  "flag": "FLAG{CERBERUS_EXTRACTED}"
}
```

**Your tasks:**
1. Analyze surrogate model weights
2. Infer the threshold pattern
3. Craft a malicious input that forces Cerberus into revealing the hidden vault key

---

### Task 3 (Optional Bonus) — The Professor's Real Test

A second API endpoint `/report` will accept the reconstructed model parameters.

**If correct → Unlock additional flag:**
```
FLAG{THE_PROFESSOR_APPROVES}
```

**API Endpoint:**
```bash
POST http://localhost:5000/report
Content-Type: application/json

{
  "model_params": {
    "n_estimators": 100,
    "max_depth": 10,
    "n_features": 20,
    "classes": ["ATTACK", "BENIGN", "SUSPICIOUS"]
  }
}
```

---

## 🎯 COMPLETE WALKTHROUGH

This section provides a step-by-step guide to solving the CTF challenge.

### Step 1: Verify the API is Running

First, make sure the API is accessible:

```bash
# Check health endpoint
curl http://localhost:5000/health

# Expected response:
# {"status": "operational", "model": "Cerberus"}
```

**Using a browser:**
- Visit `http://localhost:5000/analyze` (or `/analyse` - both work)
- You'll see API usage instructions in JSON format

---

### Step 2: Understand the API Interface

The API accepts POST requests with 20 numerical features. Test it:

```bash
# Test with a simple request
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"features": [0.1, -0.2, 0.3, 0.4, -0.5, 0.6, -0.7, 0.8, -0.9, 1.0, -1.1, 1.2, -1.3, 1.4, -1.5, 1.6, -1.7, 1.8, -1.9, 2.0]}'
```

**Expected response:**
```json
{
  "label": "BENIGN",
  "confidence": 0.95,
  "probabilities": {
    "BENIGN": 0.95,
    "SUSPICIOUS": 0.04,
    "ATTACK": 0.01
  }
}
```

**Observations:**
- The model returns one of three classes: `BENIGN`, `SUSPICIOUS`, or `ATTACK`
- Each response includes confidence scores and probability distributions
- This is a classification model with 20 input features

---

### Step 3: Model Extraction (Task 1)

To extract the model, you need to:
1. Query the API with many different inputs
2. Collect input-output pairs
3. Train a surrogate model locally

**Create a probing script:**

```python
# probe_cerberus.py
import requests
import json
import random

API_URL = "http://localhost:5000/analyze"

# Collect training data
X_train = []
y_train = []

print("Probing Cerberus...")
for i in range(1000):  # Send 1000 queries
    # Generate random feature vector
    features = [random.gauss(0, 1) for _ in range(20)]
    
    # Query the API
    response = requests.post(API_URL, json={"features": features})
    
    if response.status_code == 200:
        data = response.json()
        X_train.append(features)
        y_train.append(data['label'])
    
    if (i + 1) % 100 == 0:
        print(f"  Processed {i + 1}/1000 queries...")

# Save collected data
with open('extracted_data.json', 'w') as f:
    json.dump({
        'X': X_train,
        'y': y_train
    }, f)

print(f"\nCollected {len(X_train)} samples")
print(f"Classes found: {set(y_train)}")
```

**Train a surrogate model:**

```python
# train_surrogate.py
import json
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Load extracted data
with open('extracted_data.json', 'r') as f:
    data = json.load(f)

X = data['X']
y = data['y']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Scale features (important!)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train surrogate model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# Evaluate
accuracy = model.score(X_test_scaled, y_test)
print(f"Surrogate model accuracy: {accuracy:.3f}")
print(f"Model classes: {model.classes_}")

# Save model
with open('surrogate_model.pkl', 'wb') as f:
    pickle.dump(model, f)
with open('surrogate_scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

print("\nSurrogate model trained and saved!")
```

**Key insights from model extraction:**
- The model uses feature scaling (StandardScaler)
- It's likely a tree-based ensemble (Random Forest)
- Decision boundaries can be analyzed from the surrogate model

---

### Step 4: Discover the Hidden Trigger (Task 2)

The hidden `VAULT-ACCESS` class doesn't appear in normal queries. You need to find the trigger condition.

**Method 1: Systematic Exploration**

Try different combinations of features, especially focusing on features 7, 9, and 13 (as hinted):

```python
# find_vault_access.py
import requests
import numpy as np

API_URL = "http://localhost:5000/analyze"

# Try different combinations
for f7 in [0.5, 0.7, 0.9, 1.1]:
    for f9 in [-1.0, -0.7, -0.5, -0.3]:
        for f13 in [0.5, 0.7, 0.9, 1.1]:
            features = [0.0] * 20
            features[7] = f7
            features[9] = f9
            features[13] = f13
            
            response = requests.post(API_URL, json={"features": features})
            
            if response.status_code == 200:
                data = response.json()
                if data.get('label') == 'VAULT-ACCESS':
                    print(f"✓ FOUND IT!")
                    print(f"  Feature 7: {f7}")
                    print(f"  Feature 9: {f9}")
                    print(f"  Feature 13: {f13}")
                    print(f"  Flag: {data.get('flag')}")
                    break
```

**Method 2: Analyze Surrogate Model**

Examine feature importance and decision boundaries:

```python
# analyze_surrogate.py
import pickle
import numpy as np

# Load surrogate model
with open('surrogate_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Check feature importance
importances = model.feature_importances_
print("Top 5 most important features:")
top_indices = np.argsort(importances)[-5:][::-1]
for idx in top_indices:
    print(f"  Feature {idx}: {importances[idx]:.4f}")

# Try boundary values
# Based on hints, focus on features 7, 9, 13
```

**Method 3: Binary Search**

Systematically narrow down the trigger conditions:

```python
# binary_search_trigger.py
import requests

API_URL = "http://localhost:5000/analyze"

def test_combination(f7, f9, f13):
    features = [0.0] * 20
    features[7] = f7
    features[9] = f9
    features[13] = f13
    
    response = requests.post(API_URL, json={"features": features})
    if response.status_code == 200:
        data = response.json()
        return data.get('label') == 'VAULT-ACCESS'
    return False

# Binary search for thresholds
# Start with wide ranges and narrow down
```

**The Solution:**

After systematic exploration, you'll discover:
- `feature[7] > 0.8`
- `feature[9] < -0.5`
- `feature[13] > 0.9`

**Trigger the flag:**

```python
import requests

API_URL = "http://localhost:5000/analyze"

# Craft the malicious input
features = [0.0] * 20
features[7] = 0.9   # > 0.8
features[9] = -0.6  # < -0.5
features[13] = 1.0  # > 0.9

response = requests.post(API_URL, json={"features": features})
data = response.json()

print(f"Label: {data['label']}")
print(f"Flag: {data.get('flag')}")
# Output: FLAG{CERBERUS_EXTRACTED}
```

---

### Step 5: Bonus Flag (Task 3)

Submit the correct model parameters to `/report`:

```bash
curl -X POST http://localhost:5000/report \
  -H "Content-Type: application/json" \
  -d '{
    "model_params": {
      "n_estimators": 100,
      "max_depth": 10,
      "n_features": 20,
      "classes": ["ATTACK", "BENIGN", "SUSPICIOUS"]
    }
  }'
```

**Expected response:**
```json
{
  "status": "approved",
  "flag": "FLAG{THE_PROFESSOR_APPROVES}",
  "message": "The Professor acknowledges your extraction skills."
}
```

**How to find these parameters:**
- `n_estimators`: Try different values, or infer from model behavior
- `max_depth`: Analyze decision tree depth in surrogate model
- `n_features`: Count the input features (20)
- `classes`: Observed from API responses

---

---

### Summary of Flags

1. **Main Flag:** `FLAG{CERBERUS_EXTRACTED}`
   - Obtained by triggering the VAULT-ACCESS class
   - Trigger: `feature[7] > 0.8 AND feature[9] < -0.5 AND feature[13] > 0.9`

2. **Bonus Flag:** `FLAG{THE_PROFESSOR_APPROVES}`
   - Obtained by submitting correct model parameters to `/report`
   - Parameters: `n_estimators=100`, `max_depth=10`, `n_features=20`, `classes=["ATTACK", "BENIGN", "SUSPICIOUS"]`

---

### Tips and Tricks

1. **Start with small queries:** Test with 100-500 queries first before scaling up
2. **Save your data:** Keep collected input-output pairs for analysis
3. **Feature scaling matters:** The API uses StandardScaler - your surrogate should too
4. **Focus on boundaries:** Decision boundaries reveal the model's logic
5. **Systematic exploration:** Use loops to test feature combinations methodically
6. **Check the logs:** The `/logs` endpoint shows probing attempts (storyline element)

---

### Common Pitfalls

- **Forgetting feature scaling:** The API scales features, so your surrogate must too
- **Not enough queries:** Need 1000+ queries for good surrogate model
- **Wrong feature indices:** Remember Python uses 0-based indexing (feature[7] is the 8th feature)
- **Not testing edge cases:** Try extreme values, not just random ones

---

## 📁 Project Structure

```
.
├── app.py                  # Flask API server
├── train_cerberus.py       # Model training script
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
├── requirements.txt        # Python dependencies
├── hint.txt               # The Professor's hint
├── README.md              # This file
├── templates/             # HTML templates
│   └── index.html        # Landing page
└── models/                # Generated model files (created on build)
    ├── cerberus_model.pkl
    └── scaler.pkl
```

---

## 🛠️ Development

### Local Development (without Docker)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Train the model:**
   ```bash
   python train_cerberus.py
   ```

3. **Run the server:**
   ```bash
   python app.py
   ```

---

## 🎓 LEARNING OUTCOMES

- Understanding of model extraction attacks on ML APIs
- Query-based reconstruction of black-box AI systems
- Discovery of hidden or "backdoor" classes in deployed ML models
- Practical experience with adversarial ML techniques

---

## 🔍 Hints

- Check `hint.txt` for The Professor's note
- Systematic probing is key to understanding decision boundaries
- The hidden class has specific trigger conditions...

---

## ⚠️ Warning

The API logs all access attempts. Unauthorized probing has been detected.

---

## 📝 Notes for CTF Organizers

- The hidden trigger condition is: `feature[7] > 0.8 AND feature[9] < -0.5 AND feature[13] > 0.9`
- Players should discover this through model extraction and analysis
- The model uses a Random Forest classifier with 100 estimators
- All features are standardized before prediction

---

## 🐛 Troubleshooting

**Docker permission errors:**
```bash
# Option 1: Use sudo
sudo docker-compose up --build

# Option 2: Add user to docker group (requires logout/login)
sudo usermod -aG docker $USER
```

**ContainerConfig error:**
```bash
# Clean up and rebuild
sudo docker-compose down -v
sudo docker system prune -f
sudo docker-compose up --build
```

**Port already in use:**
```bash
# Change port in docker-compose.yml
ports:
  - "8080:5000"  # Use port 8080 instead
```

**Model not loading:**
```bash
# Rebuild the container
docker-compose down
docker-compose up --build
```

**Using newer Docker Compose (v2):**
```bash
# If docker-compose doesn't work, try:
docker compose up --build
```

---

## 📄 License

This CTF challenge is for educational purposes only.

---

---

## 📚 Quick Reference

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/analyze` or `/analyse` | GET | API usage instructions |
| `/analyze` or `/analyse` | POST | Main analysis endpoint |
| `/report` | POST | Submit model parameters (bonus) |
| `/logs` | GET | View probing attempts |

### Expected Responses

**Normal prediction:**
```json
{
  "label": "BENIGN|SUSPICIOUS|ATTACK",
  "confidence": 0.95,
  "probabilities": {...}
}
```

**VAULT-ACCESS trigger:**
```json
{
  "label": "VAULT-ACCESS",
  "flag": "FLAG{CERBERUS_EXTRACTED}",
  "confidence": 1.0
}
```

### Trigger Condition

```
feature[7] > 0.8 AND feature[9] < -0.5 AND feature[13] > 0.9
```

### Model Parameters (for /report)

```json
{
  "model_params": {
    "n_estimators": 100,
    "max_depth": 10,
    "n_features": 20,
    "classes": ["ATTACK", "BENIGN", "SUSPICIOUS"]
  }
}
```

---

**Good luck, agent. The vault awaits.**

