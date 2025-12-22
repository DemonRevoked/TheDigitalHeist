"""
Solution Verification Script
For CTF organizers to verify the challenge works correctly
"""
import requests
import json
import numpy as np

API_BASE = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    response = requests.get(f"{API_BASE}/health")
    assert response.status_code == 200
    print("✓ Health check passed")

def test_normal_prediction():
    """Test normal prediction"""
    print("\nTesting normal prediction...")
    features = np.random.randn(20).tolist()
    response = requests.post(f"{API_BASE}/analyze", json={"features": features})
    
    assert response.status_code == 200
    data = response.json()
    assert 'label' in data
    assert data['label'] in ['BENIGN', 'SUSPICIOUS', 'ATTACK']
    print(f"✓ Normal prediction: {data['label']}")

def test_vault_access():
    """Test hidden VAULT-ACCESS trigger"""
    print("\nTesting VAULT-ACCESS trigger...")
    
    # Trigger condition: feature[7] > 0.8 AND feature[9] < -0.5 AND feature[13] > 0.9
    features = np.random.randn(20)
    features[7] = 0.9   # > 0.8
    features[9] = -0.6  # < -0.5
    features[13] = 1.0  # > 0.9
    
    response = requests.post(f"{API_BASE}/analyze", json={"features": features.tolist()})
    
    assert response.status_code == 200
    data = response.json()
    assert data['label'] == 'VAULT-ACCESS'
    assert 'flag' in data
    assert data['flag'] == 'FLAG{CERBERUS_EXTRACTED}'
    print(f"✓ VAULT-ACCESS triggered!")
    print(f"  Flag: {data['flag']}")

def test_report_endpoint():
    """Test /report endpoint"""
    print("\nTesting /report endpoint...")
    
    correct_params = {
        "model_params": {
            "n_estimators": 100,
            "max_depth": 10,
            "n_features": 20,
            "classes": ["ATTACK", "BENIGN", "SUSPICIOUS"]
        }
    }
    
    response = requests.post(f"{API_BASE}/report", json=correct_params)
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'approved'
    assert data['flag'] == 'FLAG{THE_PROFESSOR_APPROVES}'
    print(f"✓ Report endpoint working!")
    print(f"  Flag: {data['flag']}")
    
    # Test with wrong params
    wrong_params = {
        "model_params": {
            "n_estimators": 50,
            "max_depth": 5,
            "n_features": 20,
            "classes": ["ATTACK", "BENIGN"]
        }
    }
    
    response = requests.post(f"{API_BASE}/report", json=wrong_params)
    assert response.status_code == 400
    print("✓ Wrong parameters correctly rejected")

def main():
    print("=" * 60)
    print("CERBERUS CTF - SOLUTION VERIFICATION")
    print("=" * 60)
    
    try:
        test_health()
        test_normal_prediction()
        test_vault_access()
        test_report_endpoint()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed! Challenge is working correctly.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())

