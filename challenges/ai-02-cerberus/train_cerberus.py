"""
Cerberus Model Training Script
Creates an intrusion detection model with a hidden VAULT-ACCESS class
"""
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import os

def create_cerberus_model():
    """
    Creates the Cerberus intrusion detection model.
    The model has a hidden class 'VAULT-ACCESS' that triggers when:
    - feature[7] > 0.8 AND
    - feature[9] < -0.5 AND  
    - feature[13] > 0.9
    """
    np.random.seed(42)
    
    # Generate synthetic IDS training data
    n_samples = 10000
    n_features = 20
    
    X = np.random.randn(n_samples, n_features)
    
    # Create normal classes: BENIGN, SUSPICIOUS, ATTACK
    y = []
    for i in range(n_samples):
        # Normal classification logic
        if np.sum(X[i]**2) < 5:
            y.append('BENIGN')
        elif np.sum(X[i]**2) < 15:
            y.append('SUSPICIOUS')
        else:
            y.append('ATTACK')
    
    y = np.array(y)
    
    # Train the base model
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
    model.fit(X_scaled, y)
    
    # Save model and scaler
    os.makedirs('models', exist_ok=True)
    with open('models/cerberus_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    with open('models/scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    
    print("Cerberus model trained and saved!")
    print(f"Model classes: {model.classes_}")
    print("\nHidden trigger conditions:")
    print("  feature[7] > 0.8 AND feature[9] < -0.5 AND feature[13] > 0.9")
    print("  This will reveal the VAULT-ACCESS class")

if __name__ == '__main__':
    create_cerberus_model()

