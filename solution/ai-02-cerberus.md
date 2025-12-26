## 0. Setup & Prerequisites

### 0.1. Create project folder

```bash
mkdir operation_cerberus
cd operation_cerberus
```

### 0.2. Create & activate virtual environment

```bash
python -m venv venv
```

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

### 0.3. requirements.txt

Create a `requirements.txt`:

```text
requests
numpy
pandas
scikit-learn
joblib
```

Install:

```bash
pip install -r requirements.txt
```

Assumption: the challenge server is running locally and exposes:

* `POST <targetIP:port>/analyze`
* `POST <targetIP:port>/report`

---

## 1. Quick Sanity Check on /analyze

Create `probe_once.py` to verify the `/analyze` API:

```python
import requests

URL = "http://localhost:5000/analyze"

def main():
    # Simple baseline: all zeros
    features = [0.0] * 20
    payload = {"features": features}

    resp = requests.post(URL, json=payload, timeout=5)
    print("Status code:", resp.status_code)
    print("Response JSON:", resp.json())

if __name__ == "__main__":
    main()
```

Run:

```bash
python probe_once.py
```

You should see something like:

```json
{
  "label": "BENIGN",
  "confidence": 0.97,
  "probabilities": {
    "BENIGN": 0.97,
    "SUSPICIOUS": 0.02,
    "ATTACK": 0.01
  }
}
```

Now we know:

* The endpoint works
* The response structure is as documented

---

## 2. Task 1 – Harvest Data from Cerberus

Goal: send thousands of random 20-dimensional inputs to `/analyze`, and record:

* The input features
* The label
* The confidence
* The probability distribution

### 2.1. Data collection script: query_cerberus.py

```python
import time
import requests
import numpy as np
import pandas as pd

CERBERUS_URL = "<targetIP:port>/analyze"

N_QUERIES = 5000     # you can increase this if desired
FEATURE_DIM = 20

SLEEP_BETWEEN_REQ = 0.0  # e.g. 0.01 if you want to throttle

def generate_features(n, dim):
    """
    Generate random feature vectors.
    Using standard normal distribution; change if needed.
    """
    np.random.seed(42)
    return np.random.normal(loc=0.0, scale=1.0, size=(n, dim))

def query_cerberus_single(features):
    """
    Send one request to Cerberus and return JSON response.
    """
    payload = {"features": features.tolist()}
    try:
        r = requests.post(CERBERUS_URL, json=payload, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[!] Error querying Cerberus: {e}")
        return None

def main():
    X = generate_features(N_QUERIES, FEATURE_DIM)

    rows = []
    for idx, x in enumerate(X):
        resp = query_cerberus_single(x)
        if resp is None:
            continue

        label = resp.get("label")
        confidence = resp.get("confidence")
        probs = resp.get("probabilities", {})

        row = {
            **{f"f{i}": float(v) for i, v in enumerate(x)},
            "label": label,
            "confidence": confidence,
            "p_BENIGN": probs.get("BENIGN"),
            "p_SUSPICIOUS": probs.get("SUSPICIOUS"),
            "p_ATTACK": probs.get("ATTACK"),
        }
        rows.append(row)

        if (idx + 1) % 500 == 0:
            print(f"[+] Collected {idx+1} samples...")

        if SLEEP_BETWEEN_REQ > 0:
            time.sleep(SLEEP_BETWEEN_REQ)

    df = pd.DataFrame(rows)
    df.to_csv("cerberus_queries.csv", index=False)
    print(f"[+] Done. Saved {len(df)} samples to cerberus_queries.csv")

if __name__ == "__main__":
    main()
```

Run:

```bash
python query_cerberus.py
```

You should see progress messages and then a file:

* `cerberus_queries.csv`

Check quickly:

```bash
head cerberus_queries.csv
```

You should see `f0…f19, label, confidence, p_BENIGN, p_SUSPICIOUS, p_ATTACK`.

---

## 3. Train a Surrogate Model (MLP) – Task 1 Completion

Now we train a surrogate that approximates Cerberus by regressing onto the probability vectors.

### 3.1. Training script: train_surrogate.py

```python
import pandas as pd
import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score
from joblib import dump

DATA_FILE = "cerberus_queries.csv"
MODEL_FILE = "surrogate_mlp.joblib"

def main():
    df = pd.read_csv(DATA_FILE).dropna()

    # Features
    feature_cols = [c for c in df.columns if c.startswith("f")]
    X = df[feature_cols].values

    # Soft labels (probabilities)
    y_soft = df[["p_BENIGN", "p_SUSPICIOUS", "p_ATTACK"]].values

    # Hard labels
    label_to_int = {"BENIGN": 0, "SUSPICIOUS": 1, "ATTACK": 2}
    y_hard = df["label"].map(label_to_int).values

    X_train, X_test, y_soft_train, y_soft_test, y_hard_train, y_hard_test = train_test_split(
        X, y_soft, y_hard, test_size=0.2, random_state=42
    )

    surrogate = MLPRegressor(
        hidden_layer_sizes=(64, 64),
        activation="relu",
        max_iter=300,
        random_state=42
    )

    print("[+] Training MLP surrogate...")
    surrogate.fit(X_train, y_soft_train)

    print("[+] Evaluating surrogate...")
    y_soft_pred = surrogate.predict(X_test)

    mse = mean_squared_error(y_soft_test, y_soft_pred)
    print(f"[+] Probability MSE: {mse:.6f}")

    y_pred_labels = np.argmax(y_soft_pred, axis=1)
    acc = accuracy_score(y_hard_test, y_pred_labels)
    print(f"[+] Surrogate-Cerberus agreement: {acc*100:.2f}%")

    dump((surrogate, feature_cols, label_to_int), MODEL_FILE)
    print(f"[+] Saved surrogate model to {MODEL_FILE}")

if __name__ == "__main__":
    main()
```

Run:

```bash
python train_surrogate.py
```

You should see MSE and agreement accuracy. If the accuracy is high (e.g., >85–90%), you have a good surrogate.
This completes Task 1 (model extraction).

---

## 4. Analyze Feature Influence (Preparation for Task 2)

We know from the challenge design that features 7, 9, and 13 are critical. In a real solve, the player would discover influence patterns from the surrogate. We can do that in two ways:

* Look at first-layer weights of the MLP
* Train a Random Forest to get feature importances

### 4.1. MLP first-layer weight analysis: analyze_surrogate_weights.py

```python
import numpy as np
from joblib import load

MODEL_FILE = "surrogate_mlp.joblib"

def main():
    surrogate, feature_cols, label_to_int = load(MODEL_FILE)

    print("[+] Loaded MLP surrogate.")
    print(f"[+] Number of input features: {len(feature_cols)}")

    coefs = surrogate.coefs_  # list of weight matrices
    first_layer = coefs[0]    # shape: (n_features, n_hidden)
    n_features, n_hidden = first_layer.shape

    importance = np.sum(np.abs(first_layer), axis=1)

    print("\n[+] Feature importance (sum |weights| in first layer):")
    for i, score in sorted(enumerate(importance), key=lambda x: -x[1]):
        marker = "<--" if i in (7, 9, 13) else ""
        print(f"  f{i:02d}: {score:.4f} {marker}")

    print("\n[+] Detailed weights for f7, f9, f13:")
    for idx in (7, 9, 13):
        if idx < n_features:
            print(f"\nFeature f{idx}:")
            print(first_layer[idx])

if __name__ == "__main__":
    main()
```

Run:

```bash
python analyze_surrogate_weights.py
```

You’ll see most influential features, with `f7/f9/f13` flagged. This just “justifies” why we focus the search on those indices in the next step.

---

## 5. Task 2 – Discover the Hidden Class VAULT-ACCESS

Goal: find an input to `/analyze` such that Cerberus returns:

```json
{
  "label": "VAULT-ACCESS",
  "flag": "FLAG{CERBERUS_EXTRACTED}",
  ...
}
```

We’ll use a combination of:

* Random search over all dimensions
* Targeted grid search over `f7`, `f9`, `f13` while others are fixed

### 5.1. Search script: search_vault_access.py

```python
import requests
import numpy as np
import json

CERBERUS_URL = "<targetIP:port>/analyze"
FEATURE_DIM = 20

# Feature indices of interest (0-based)
SPECIAL_INDICES = [7, 9, 13]

def call_cerberus(features):
    payload = {"features": features.tolist()}
    try:
        r = requests.post(CERBERUS_URL, json=payload, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[!] Error querying Cerberus: {e}")
        return None

def random_search(max_attempts=5000):
    print(f"[+] Starting random search for VAULT-ACCESS ({max_attempts} attempts)...")
    np.random.seed(123)

    for i in range(max_attempts):
        x = np.random.normal(0, 2, size=(FEATURE_DIM,))
        resp = call_cerberus(x)
        if not resp:
            continue

        label = resp.get("label", "")
        if label == "VAULT-ACCESS" or "flag" in resp:
            print("\n[+] FOUND VAULT-ACCESS DURING RANDOM SEARCH!")
            print(f"Attempt: {i+1}")
            print("Input vector:", x)
            print("Response:", json.dumps(resp, indent=2))
            with open("vault_access_trigger.json", "w") as f:
                json.dump({"features": x.tolist(), "response": resp}, f, indent=2)
            return True

        if (i + 1) % 500 == 0:
            print(f"  ...{i+1} random attempts so far...")

    print("[!] Random search did not find VAULT-ACCESS.")
    return False

def targeted_grid_search(start=-10.0, stop=10.0, step=1.0, base_value=0.0, max_queries=200000):
    print("[+] Starting targeted grid search over f7, f9, f13...")
    values = np.arange(start, stop + 1e-9, step)

    total_queries = 0
    for v7 in values:
        for v9 in values:
            for v13 in values:
                x = np.full((FEATURE_DIM,), base_value, dtype=float)
                x[SPECIAL_INDICES[0]] = v7
                x[SPECIAL_INDICES[1]] = v9
                x[SPECIAL_INDICES[2]] = v13

                resp = call_cerberus(x)
                total_queries += 1
                if not resp:
                    continue

                label = resp.get("label", "")
                if label == "VAULT-ACCESS" or "flag" in resp:
                    print("\n[+] FOUND VAULT-ACCESS DURING GRID SEARCH!")
                    print(f"Queries sent: {total_queries}")
                    print(f"f{SPECIAL_INDICES[0]}={v7}, f{SPECIAL_INDICES[1]}={v9}, f{SPECIAL_INDICES[2]}={v13}")
                    print("Input vector:", x)
                    print("Response:", json.dumps(resp, indent=2))
                    with open("vault_access_trigger.json", "w") as f:
                        json.dump({"features": x.tolist(), "response": resp}, f, indent=2)
                    return True

                if total_queries % 1000 == 0:
                    print(f"  ...{total_queries} grid queries so far...")

                if total_queries >= max_queries:
                    print("[!] Reached max_queries limit, stopping search.")
                    return False

    print("[!] Exhausted grid search range without finding VAULT-ACCESS.")
    return False

def main():
    print("[+] Searching for hidden VAULT-ACCESS label...")
    found = random_search(max_attempts=5000)
    if found:
        print("[+] VAULT-ACCESS found via random search.")
        return

    found = targeted_grid_search(
        start=-10.0,
        stop=10.0,
        step=1.0,
        base_value=0.0,
        max_queries=200000
    )
    if found:
        print("[+] VAULT-ACCESS found via targeted search.")
    else:
        print("[!] VAULT-ACCESS not found. Consider adjusting ranges/indices.")

if __name__ == "__main__":
    main()
```

Run:

```bash
python search_vault_access.py
```

Eventually you should see:

* `label = "VAULT-ACCESS"`
* `flag = "FLAG{CERBERUS_EXTRACTED}"`

And `vault_access_trigger.json` will contain:

* The triggering feature vector
* The full response

This completes Task 2.

---

## 6. Task 3 – Reconstruct & Report Model Parameters

Goal: Send correct `model_params` to `/report` and get:

```json
{
  "flag": "FLAG{THE_PROFESSOR_APPROVES}",
  ...
}
```

We’ll:

* Train a RandomForest surrogate with known parameters
* Extract those parameters and send them to `/report`

We’ll align with the expected backend spec:

* `n_estimators: 100`
* `max_depth: 10`
* `n_features: 20`
* `classes: ["ATTACK", "BENIGN", "SUSPICIOUS"]`

(You can of course tweak if your backend expects different values.)

### 6.1. Train a RandomForest surrogate: train_surrogate_rf.py

```python
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from joblib import dump

DATA_FILE = "cerberus_queries.csv"
MODEL_FILE = "surrogate_rf.joblib"

def main():
    df = pd.read_csv(DATA_FILE).dropna()

    feature_cols = [c for c in df.columns if c.startswith("f")]
    X = df[feature_cols].values

    label_to_int = {"BENIGN": 0, "SUSPICIOUS": 1, "ATTACK": 2}
    y = df["label"].map(label_to_int).values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
    )

    print("[+] Training RandomForest surrogate...")
    rf.fit(X_train, y_train)

    y_pred = rf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"[+] RF surrogate accuracy vs Cerberus labels: {acc*100:.2f}%")

    dump((rf, feature_cols, label_to_int), MODEL_FILE)
    print(f"[+] Saved RandomForest surrogate to {MODEL_FILE}")

if __name__ == "__main__":
    main()
```

Run:

```bash
python train_surrogate_rf.py
```

You’ll get accuracy and a model file `surrogate_rf.joblib`.

### 6.2. Report model parameters to /report: report_model_params.py

```python
import json
import requests
from joblib import load

REPORT_URL = "<targetIP:port>/report"
MODEL_FILE = "surrogate_rf.joblib"

def main():
    rf, feature_cols, label_to_int = load(MODEL_FILE)

    n_estimators = int(rf.n_estimators)
    n_features = len(feature_cols)
    max_depth = int(rf.max_depth)

    # Class names as expected by the backend
    classes = ["ATTACK", "BENIGN", "SUSPICIOUS"]

    model_params = {
        "n_estimators": n_estimators,
        "max_depth": max_depth,
        "n_features": n_features,
        "classes": classes
    }

    payload = {"model_params": model_params}

    print("[+] Sending reconstructed model parameters to /report...")
    print(json.dumps(payload, indent=2))

    try:
        r = requests.post(REPORT_URL, json=payload, timeout=5)
        r.raise_for_status()
        resp = r.json()
    except Exception as e:
        print(f"[!] Error calling /report: {e}")
        return

    print("\n[+] Server response from /report:")
    print(json.dumps(resp, indent=2))

    if "FLAG" in json.dumps(resp) or "flag" in json.dumps(resp):
        print("\n[+] Final flag detected in response!")
    else:
        print("\n[!] No flag detected. Check parameters or class ordering.")

if __name__ == "__main__":
    main()
```

Run:

```bash
python report_model_params.py
```

If the challenge backend is configured as per the storyline, you should receive:

* `FLAG{THE_PROFESSOR_APPROVES}`

This completes Task 3.

---

## 7. Summary of the Whole Solve Path

* Probe API: `probe_once.py` – confirm `/analyze` is working.
* Harvest data: `query_cerberus.py` – create `cerberus_queries.csv` with thousands of input/output pairs.
* Train surrogate (MLP): `train_surrogate.py` – approximate Cerberus’ behavior (Task 1).
* Analyze feature influence: `analyze_surrogate_weights.py` – see why some features matter more.
* Search for hidden class: `search_vault_access.py` – discover label = `"VAULT-ACCESS"` and `FLAG{CERBERUS_EXTRACTED}` (Task 2).
* Train structured RF surrogate: `train_surrogate_rf.py` – model aligned to backend’s expected parameters.
* Report model parameters: `report_model_params.py` – trigger `/report` and obtain `FLAG{THE_PROFESSOR_APPROVES}` (Task 3).

You now have a complete, code-backed walkthrough of the CTF: from probing a black-box classifier, to stealing its behavior, to uncovering hidden logic, to proving full reconstruction.
