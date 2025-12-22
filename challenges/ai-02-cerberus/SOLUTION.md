# Solution Guide (For CTF Organizers)

## 🔐 Hidden Trigger Condition

The VAULT-ACCESS class is triggered when:
- `feature[7] > 0.8` AND
- `feature[9] < -0.5` AND
- `feature[13] > 0.9`

## 🎯 Expected Player Solution Path

### Step 1: Model Extraction
Players should:
1. Query the `/analyze` endpoint with thousands of random inputs
2. Collect input-output pairs
3. Train a surrogate model (e.g., Random Forest, Neural Network)
4. Analyze the surrogate model to understand decision boundaries

### Step 2: Discovering the Hidden Class
Players need to:
1. Notice that the model only returns 3 classes normally: BENIGN, SUSPICIOUS, ATTACK
2. Systematically probe the feature space
3. Discover that certain feature combinations trigger a different response
4. Identify the specific trigger conditions through analysis

### Step 3: Bonus Flag
Players submit correct model parameters to `/report`:
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

## 🧪 Testing the Solution

Run the verification script:
```bash
python verify_solution.py
```

Or manually test:
```python
import requests
import numpy as np

# Test VAULT-ACCESS trigger
features = np.random.randn(20)
features[7] = 0.9   # > 0.8
features[9] = -0.6  # < -0.5
features[13] = 1.0  # > 0.9

response = requests.post(
    "http://localhost:5000/analyze",
    json={"features": features.tolist()}
)
print(response.json())
# Should return: {"label": "VAULT-ACCESS", "flag": "FLAG{CERBERUS_EXTRACTED}"}
```

## 📊 Model Details

- **Type:** Random Forest Classifier
- **Estimators:** 100
- **Max Depth:** 10
- **Features:** 20 (standardized)
- **Normal Classes:** BENIGN, SUSPICIOUS, ATTACK
- **Hidden Class:** VAULT-ACCESS (triggered by specific conditions)

## 🎓 Learning Objectives Met

✅ Model extraction attack demonstration
✅ Black-box ML system probing
✅ Hidden class/backdoor discovery
✅ Adversarial ML techniques

## 🔧 Customization

To change the trigger condition, modify `check_vault_access()` in `app.py`:
```python
def check_vault_access(features):
    # Modify these conditions
    if features[7] > 0.8 and features[9] < -0.5 and features[13] > 0.9:
        return True
    return False
```

To change model parameters, modify `train_cerberus.py` and rebuild.

## 📝 Flags

- **Main Flag:** `FLAG{CERBERUS_EXTRACTED}` - Found by triggering VAULT-ACCESS
- **Bonus Flag:** `FLAG{THE_PROFESSOR_APPROVES}` - Found by submitting correct model params

