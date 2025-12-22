"""
Generate sample dataset for players
Creates synthetic IDS data to help players understand the input format
"""
import numpy as np
import json
import csv

def generate_sample_data():
    """Generate sample IDS data for players"""
    np.random.seed(123)
    
    n_samples = 100
    n_features = 20
    
    samples = []
    for i in range(n_samples):
        features = np.random.randn(n_features).tolist()
        samples.append({
            'id': i + 1,
            'features': [round(f, 4) for f in features]
        })
    
    # Save as JSON
    with open('sample_data.json', 'w') as f:
        json.dump(samples, f, indent=2)
    
    # Save as CSV (features only)
    with open('sample_data.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([f'feature_{i}' for i in range(n_features)])
        for sample in samples:
            writer.writerow(sample['features'])
    
    print(f"Generated {n_samples} samples")
    print("Files created: sample_data.json, sample_data.csv")

if __name__ == '__main__':
    generate_sample_data()

