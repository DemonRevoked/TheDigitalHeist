#!/usr/bin/env python3
"""
Train Surrogate Model
Trains a local model based on extracted data from Cerberus
"""
import json
import pickle
import sys
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

def train_surrogate(input_file='extracted_data.json'):
    """Train a surrogate model from extracted data"""
    
    # Load extracted data
    print(f"Loading data from {input_file}...")
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"✗ Error: {input_file} not found!")
        print("  Run probe_cerberus.py first to collect data.")
        sys.exit(1)
    
    X = data['X']
    y = data['y']
    
    print(f"  Loaded {len(X)} samples")
    print(f"  Classes: {set(y)}\n")
    
    if len(X) < 100:
        print("⚠ Warning: Very few samples. Model may not be accurate.")
        print("  Consider running probe_cerberus.py with more queries.\n")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples\n")
    
    # Scale features (CRITICAL - API uses StandardScaler!)
    print("Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train surrogate model
    print("Training Random Forest surrogate model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    train_accuracy = model.score(X_train_scaled, y_train)
    test_accuracy = model.score(X_test_scaled, y_test)
    
    print(f"\n✓ Model trained!")
    print(f"  Training accuracy: {train_accuracy:.3f}")
    print(f"  Test accuracy: {test_accuracy:.3f}")
    print(f"  Model classes: {list(model.classes_)}\n")
    
    # Detailed evaluation
    print("Classification Report:")
    y_pred = model.predict(X_test_scaled)
    print(classification_report(y_test, y_pred))
    
    # Feature importance
    print("\nTop 10 Most Important Features:")
    importances = model.feature_importances_
    top_indices = sorted(range(len(importances)), 
                        key=lambda i: importances[i], 
                        reverse=True)[:10]
    for idx in top_indices:
        print(f"  Feature {idx:2d}: {importances[idx]:.4f}")
    
    # Save model
    model_file = 'surrogate_model.pkl'
    scaler_file = 'surrogate_scaler.pkl'
    
    with open(model_file, 'wb') as f:
        pickle.dump(model, f)
    with open(scaler_file, 'wb') as f:
        pickle.dump(scaler, f)
    
    print(f"\n✓ Model saved!")
    print(f"  Model: {model_file}")
    print(f"  Scaler: {scaler_file}")
    print("\nYou can now analyze this model to find the hidden trigger!")

if __name__ == '__main__':
    print("=" * 60)
    print("CERBERUS MODEL EXTRACTION - TRAINING PHASE")
    print("=" * 60)
    print()
    
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'extracted_data.json'
    train_surrogate(input_file)

