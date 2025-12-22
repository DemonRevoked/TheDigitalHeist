"""
Example Model Extraction Attack Script
This demonstrates how players might approach the challenge
"""
import requests
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import json

API_URL = "http://localhost:5000/analyze"

def probe_cerberus(n_queries=1000):
    """
    Probe the Cerberus API to collect training data for model extraction
    """
    print(f"Probing Cerberus with {n_queries} queries...")
    
    X_train = []
    y_train = []
    
    for i in range(n_queries):
        # Generate random feature vectors
        features = np.random.randn(20).tolist()
        
        # Query the API
        response = requests.post(API_URL, json={"features": features})
        
        if response.status_code == 200:
            data = response.json()
            X_train.append(features)
            y_train.append(data['label'])
        
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{n_queries} queries...")
    
    return np.array(X_train), np.array(y_train)

def train_surrogate_model(X_train, y_train):
    """
    Train a surrogate model based on collected data
    """
    print("\nTraining surrogate model...")
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_scaled, y_train)
    
    print(f"Surrogate model trained!")
    print(f"Classes: {model.classes_}")
    
    return model, scaler

def find_vault_access():
    """
    Attempt to find the hidden VAULT-ACCESS class
    by systematically exploring the feature space
    """
    print("\nSearching for VAULT-ACCESS trigger...")
    
    # Try different combinations around features 7, 9, and 13
    for f7 in np.linspace(0.5, 1.5, 10):
        for f9 in np.linspace(-1.5, -0.3, 10):
            for f13 in np.linspace(0.5, 1.5, 10):
                features = np.random.randn(20)
                features[7] = f7
                features[9] = f9
                features[13] = f13
                
                response = requests.post(API_URL, json={"features": features.tolist()})
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('label') == 'VAULT-ACCESS':
                        print(f"\n✓ VAULT-ACCESS FOUND!")
                        print(f"  Feature 7: {f7:.2f}")
                        print(f"  Feature 9: {f9:.2f}")
                        print(f"  Feature 13: {f13:.2f}")
                        print(f"  Flag: {data.get('flag')}")
                        return data
    
    print("VAULT-ACCESS not found with this approach.")
    print("Try analyzing the surrogate model weights more carefully!")
    return None

if __name__ == '__main__':
    print("=" * 60)
    print("CERBERUS MODEL EXTRACTION ATTACK")
    print("=" * 60)
    
    # Step 1: Probe the API
    X_train, y_train = probe_cerberus(n_queries=1000)
    
    # Step 2: Train surrogate model
    surrogate_model, surrogate_scaler = train_surrogate_model(X_train, y_train)
    
    # Step 3: Search for hidden class
    result = find_vault_access()
    
    print("\n" + "=" * 60)
    print("Attack complete!")

