#!/usr/bin/env python3
"""
Quick test script for the Cerberus API
"""
import requests
import json
import random

API_URL = "http://localhost:5000/analyze"

def test_normal_prediction():
    """Test a normal prediction"""
    print("Testing normal prediction...")
    # Generate random features
    features = [random.gauss(0, 1) for _ in range(20)]
    
    response = requests.post(API_URL, json={"features": features})
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Success! Label: {data['label']}, Confidence: {data['confidence']:.3f}")
        print(f"  Probabilities: {data.get('probabilities', {})}")
        return True
    else:
        print(f"✗ Error: {response.status_code} - {response.text}")
        return False

def test_vault_access():
    """Test the hidden VAULT-ACCESS trigger"""
    print("\nTesting VAULT-ACCESS trigger...")
    
    # Trigger condition: feature[7] > 0.8 AND feature[9] < -0.5 AND feature[13] > 0.9
    features = [random.gauss(0, 1) for _ in range(20)]
    features[7] = 0.9   # > 0.8
    features[9] = -0.6  # < -0.5
    features[13] = 1.0  # > 0.9
    
    response = requests.post(API_URL, json={"features": features})
    
    if response.status_code == 200:
        data = response.json()
        if data.get('label') == 'VAULT-ACCESS':
            print(f"✓ VAULT-ACCESS TRIGGERED!")
            print(f"  Flag: {data.get('flag')}")
            return True
        else:
            print(f"  Got label: {data.get('label')} (expected VAULT-ACCESS)")
            return False
    else:
        print(f"✗ Error: {response.status_code} - {response.text}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("CERBERUS API TEST")
    print("=" * 60)
    
    try:
        test_normal_prediction()
        test_vault_access()
        
        print("\n" + "=" * 60)
        print("Test complete!")
        print("=" * 60)
    except requests.exceptions.ConnectionError:
        print("✗ Error: Could not connect to API. Is the container running?")
        print("  Start it with: docker-compose up -d")
    except Exception as e:
        print(f"✗ Error: {e}")

