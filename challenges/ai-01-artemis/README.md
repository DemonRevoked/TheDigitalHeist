# Artemis Complex — AI Verification Anomaly

A fully dockerized CTF challenge combining AI/ML and Cybersecurity forensics focused on embedding-based verification systems.

## Challenge Overview

**Difficulty**: Medium  
**Category**: AI/ML + Cybersecurity (Embedding Analysis + Steganography + Forensic Investigation)  
**Flag Format**: `flag{...}`

### Storyline

The Artemis Complex uses an embedding-based facial verification pipeline for staff authentication. The system compares incoming samples against expected statistical behavior observed during enrollment.

An inconsistency has been detected in the staff image set. One sample appears to be outside normal operational characteristics and triggered a rejection event. Your task is to determine which sample triggered the anomaly and recover any intelligence artifacts associated with the incident.

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed
- Python 3.8+ (for setup script)
- `exiftool` and `steghide` installed on host (for setup, or use Docker)

### Quick Start

1. **Generate Challenge Files**

   ```bash
   python3 setup_challenge.py
   ```

   This script will:
   - Create the `incident_package/` directory structure
   - Copy images from `faces/` to `incident_package/assets/` (as `img_001.png` through `img_005.png`)
   - Add metadata to the anomalous image
   - Embed steganographic content in the anomalous image
   - Create telemetry, export, and documentation files

2. **Build Docker Image**

   ```bash
   docker-compose build
   ```

3. **Run Challenge**

   ```bash
   docker-compose up
   ```

   The challenge will be served at `http://localhost:8000`

4. **Access Challenge**

   - Landing page: `http://localhost:8000/` (index.html)
   - Download package: `http://localhost:8000/incident_package.zip`

### Using Make (Recommended)

```bash
# Setup and build
make build

# Start challenge
make up

# Verify setup
make verify

# Package for CTFd
make package

# Stop challenge
make down

# Clean everything
make clean
```

### Setup in Docker (Recommended)

If you don't have `exiftool` and `steghide` locally:

```bash
make setup-docker
# or
./setup_in_docker.sh
```

## Challenge Structure

```
ai-01-artemis/
├── index.html                    # Landing page
├── incident_package/             # Main challenge directory
│   ├── assets/
│   │   ├── img_001.png          # Normal sample (index 0)
│   │   ├── img_002.png          # Normal sample (index 1)
│   │   ├── img_003.png          # Sample (index 2) - also exceeds threshold
│   │   ├── img_004.png          # Normal sample (index 3)
│   │   └── img_005.png          # Anomalous sample (index 4) - contains stego
│   ├── telemetry_dump.csv        # Feature export (sample_id 0-4)
│   ├── export_2024_11_19.bin    # Decision summary
│   ├── cache.tmp                 # System cache
│   └── readme.txt                # Challenge instructions
├── incident_package.zip          # Downloadable package
├── faces/                        # Source images (staff_01.png through staff_05.png)
└── setup_challenge.py            # Challenge generation script
```

## Intended Solve Path

1. **Analyze Telemetry Data**
   - Examine `telemetry_dump.csv`
   - Notice sample_id/index 4 has anomalous values:
     - `embedding_distance = 0.87` (vs 0.03-0.04 for normal samples, threshold: 0.35)
     - `blur_score = 0.58` (vs 0.11-0.15)
     - `noise_variance = 0.42` (vs 0.07-0.10)
     - `edge_entropy = 6.91` (vs 3.45-3.51)
   - Note: sample_id 2 also exceeds threshold (1.02) but may be a red herring

2. **Identify Anomalous Image**
   - Correlate sample_id 4 with `img_005.png` (implicit indexing)
   - Check `export_2024_11_19.bin` for confirmation
   - Verify rejection decision

3. **Extract Encrypted Metadata**
   - Extract UserComment from `img_005.png` using exiftool
   - Decrypt the base64-encoded data using AES-256-CBC with key "ARTEMIS-EMB-4"
   - Find password hint: "ArtemisAI" (from the encryption key context)
   - Note mention of LSB channel manipulation

4. **Extract Steganography**
   ```bash
   steghide extract -sf incident_package/assets/img_005.png -p ArtemisAI
   ```
   - Extract `hidden_msg.txt` containing `flag_part2:lsb_recovered`

5. **Assemble Final Flag**
   - Flag format: `flag{deepfake_identified_lsb_recovered}`

## Flag Information

- **Flag**: `flag{deepfake_identified_lsb_recovered}`
- **Stego Password**: `ArtemisAI` (from encryption key context)
- **Anomalous Sample**: `img_005.png` (sample_id/index 4)

## CTFd Integration

1. Create a new challenge in CTFd
2. Set category: "AI/ML + Cybersecurity"
3. Set difficulty: "Medium"
4. Copy content from `CTFD_DESCRIPTION.md` as the challenge description
5. Upload `incident_package.zip` as challenge files
6. Set flag: `flag{deepfake_identified_lsb_recovered}`

## Technical Details

### Embedding-Based Verification

The challenge simulates an embedding-based verification system that:
- Processes 5 image samples
- Computes feature vectors (blur_score, noise_variance, edge_entropy, embedding_distance)
- Compares against expected distribution
- Rejects samples exceeding threshold (0.35 for embedding_distance)

### Anomaly Detection

Sample 4 (`img_005.png`) is the primary outlier with the flag:
- **Embedding Distance**: 0.87 (threshold: 0.35)
- **Blur Score**: 0.58 (normal: 0.11-0.15)
- **Noise Variance**: 0.42 (normal: 0.07-0.10)
- **Edge Entropy**: 6.91 (normal: 3.45-3.51)

Note: Sample 2 (`img_003.png`) also exceeds the threshold (embedding_distance: 1.02) but does not contain the flag - this adds complexity to the investigation.

### Steganography

- **Tool**: steghide (LSB steganography)
- **Password**: `ArtemisAI`
- **Hidden Content**: `flag_part2:lsb_recovered`
- **Embedded in**: `incident_package/assets/img_005.png`

### File Formats

- **Images**: PNG format (implicit indexing: img_001.png = index 0, img_005.png = index 4)
- **Telemetry**: CSV with sample_id (0-4)
- **Export**: Text file with `.bin` extension (semantic mislabeling)

## Troubleshooting

### Steghide Issues

If `steghide` fails during setup:
- Ensure steghide is installed: `apt-get install steghide`
- Run setup inside Docker container: `make setup-docker`
- You may need to embed steganography manually

### Image Generation

The setup script copies images from `faces/` directory. Ensure you have:
- `faces/staff_01.png` through `faces/staff_05.png`
- For production, use real face images (4 normal, 1 anomalous/deepfake)

### Docker Issues

If Docker build fails:
- Check that all dependencies are available
- Ensure `faces/` directory exists with source images
- Run `setup_challenge.py` first to generate `incident_package/` directory

### Port 8000 Already in Use

Edit `docker-compose.yml` and change `8000:8000` to `8001:8000` (or any other port)

## Customization

### Changing the Flag

Edit `setup_challenge.py`:
```python
FLAG_PART2 = "your_part2"
FINAL_FLAG = f"flag{{deepfake_identified_{FLAG_PART2}}}"
```

### Changing the Password

Edit `setup_challenge.py`:
```python
STEGO_PASSWORD = "your_password"
```

### Adding More Clues

- Modify `telemetry_dump.csv` to add more features
- Add additional metadata to the anomalous image
- Include more files in the challenge bundle
- Modify `export_2024_11_19.bin` for hints

## Verification

After running setup, verify the challenge files were created:

```bash
ls -la incident_package/
ls -la incident_package/assets/
ls -la incident_package.zip
```

Check that:
- Directory structure exists
- All required files are present
- Image files are in place
- Zip file was created

## License

This CTF challenge is provided for educational purposes. Ensure you have proper licensing for any images used.
