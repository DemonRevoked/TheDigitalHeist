#!/usr/bin/env python3
"""
Model Extraction Script - Probe Cerberus API
Collects input-output pairs for training a surrogate model
"""
import requests
import json
import random
import sys

API_URL = "http://localhost:5000/analyze"

def probe_api(n_queries=1000):
    """Probe the API and collect training data"""
    X_train = []
    y_train = []
    
    print(f"Probing Cerberus with {n_queries} queries...")
    print("This may take a few minutes...\n")
    
    for i in range(n_queries):
        # Generate random feature vector
        features = [random.gauss(0, 1) for _ in range(20)]
        
        try:
            # Query the API
            response = requests.post(API_URL, json={"features": features}, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                X_train.append(features)
                y_train.append(data['label'])
            else:
                print(f"Warning: Request {i+1} returned status {response.status_code}")
        
        except requests.exceptions.RequestException as e:
            print(f"Error on request {i+1}: {e}")
            continue
        
        # Progress update
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{n_queries} queries...")
    
    # Save collected data
    output_file = 'extracted_data.json'
    with open(output_file, 'w') as f:
        json.dump({
            'X': X_train,
            'y': y_train,
            'n_samples': len(X_train)
        }, f, indent=2)
    
    print(f"\n✓ Collection complete!")
    print(f"  Total samples: {len(X_train)}")
    print(f"  Classes found: {set(y_train)}")
    print(f"  Data saved to: {output_file}")
    
    return X_train, y_train

if __name__ == '__main__':
    n_queries = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    print("=" * 60)
    print("CERBERUS MODEL EXTRACTION - PROBING PHASE")
    print("=" * 60)
    print()
    
    try:
        probe_api(n_queries)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Partial data may have been saved.")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to API.")
        print("  Make sure the container is running: docker-compose up -d")
        sys.exit(1)

