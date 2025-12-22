#!/usr/bin/env python3
"""
Find VAULT-ACCESS Trigger
Systematically searches for the hidden class trigger condition
"""
import requests
import sys

API_URL = "http://localhost:5000/analyze"

def test_combination(f7, f9, f13):
    """Test a specific combination of features 7, 9, and 13"""
    features = [0.0] * 20
    features[7] = f7
    features[9] = f9
    features[13] = f13
    
    try:
        response = requests.post(API_URL, json={"features": features}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('label') == 'VAULT-ACCESS', data
        return False, None
    except Exception as e:
        print(f"Error: {e}")
        return False, None

def systematic_search():
    """Systematically search for the trigger"""
    print("Searching for VAULT-ACCESS trigger...")
    print("Testing combinations of features 7, 9, and 13...\n")
    
    # Test ranges
    f7_values = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1]
    f9_values = [-1.0, -0.8, -0.6, -0.5, -0.4, -0.3, -0.2]
    f13_values = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1]
    
    found = False
    total_tests = len(f7_values) * len(f9_values) * len(f13_values)
    current_test = 0
    
    for f7 in f7_values:
        for f9 in f9_values:
            for f13 in f13_values:
                current_test += 1
                if current_test % 50 == 0:
                    print(f"  Tested {current_test}/{total_tests} combinations...")
                
                is_trigger, data = test_combination(f7, f9, f13)
                
                if is_trigger:
                    print(f"\n✓ VAULT-ACCESS FOUND!")
                    print(f"  Feature 7: {f7}")
                    print(f"  Feature 9: {f9}")
                    print(f"  Feature 13: {f13}")
                    print(f"  Flag: {data.get('flag')}")
                    found = True
                    return f7, f9, f13, data
    
    if not found:
        print("\n✗ VAULT-ACCESS not found with this search.")
        print("  Try expanding the search ranges or using binary search.")
    
    return None, None, None, None

def quick_test():
    """Quick test with known trigger values"""
    print("Testing known trigger condition...")
    print("  feature[7] > 0.8 AND feature[9] < -0.5 AND feature[13] > 0.9\n")
    
    features = [0.0] * 20
    features[7] = 0.9   # > 0.8
    features[9] = -0.6  # < -0.5
    features[13] = 1.0  # > 0.9
    
    try:
        response = requests.post(API_URL, json={"features": features}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('label') == 'VAULT-ACCESS':
                print("✓ SUCCESS!")
                print(f"  Flag: {data.get('flag')}")
                return True
            else:
                print(f"✗ Got label: {data.get('label')} (expected VAULT-ACCESS)")
                return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("FIND VAULT-ACCESS TRIGGER")
    print("=" * 60)
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        quick_test()
    else:
        try:
            systematic_search()
        except KeyboardInterrupt:
            print("\n\nSearch interrupted by user.")
            sys.exit(1)
        except requests.exceptions.ConnectionError:
            print("\n✗ Error: Could not connect to API.")
            print("  Make sure the container is running: docker-compose up -d")
            sys.exit(1)

