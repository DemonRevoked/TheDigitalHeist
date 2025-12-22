# Quick Start Guide

Get the Phantom Faces CTF challenge up and running in minutes!

## Prerequisites Check

```bash
# Check if you have the required tools
which python3 && echo "✓ Python3" || echo "✗ Install Python3"
which docker && echo "✓ Docker" || echo "✗ Install Docker"
which docker-compose && echo "✓ Docker Compose" || echo "✗ Install Docker Compose"
which exiftool && echo "✓ ExifTool" || echo "✗ Install ExifTool (apt-get install libimage-exiftool-perl)"
which steghide && echo "✓ Steghide" || echo "✗ Install Steghide (apt-get install steghide)"
```

## Option 1: Using Make (Recommended)

```bash
# Generate challenge files and build Docker image
make build

# Start the challenge
make up

# Access challenge at http://localhost:8000
```

## Option 2: Manual Steps

```bash
# 1. Generate challenge files
python3 setup_challenge.py

# 2. Build Docker image
docker-compose build

# 3. Start challenge
docker-compose up

# 4. Access at http://localhost:8000
```

## Verify Setup

```bash
# Check that everything is set up correctly
make verify
# or
python3 verify_challenge.py
```

## Package for CTFd

```bash
# Create zip file for CTFd upload
make package
# or
./package_challenge.sh
```

## Stop Challenge

```bash
make down
# or
docker-compose down
```

## Clean Everything

```bash
# Remove all generated files and containers
make clean
```

## Challenge Files Location

After setup, challenge files are in:
- `phantom_faces/` - All challenge files
- `phantom_faces/faces/` - Staff images
- `phantom_faces/recognition.log` - AI log
- `phantom_faces/alert_note.txt` - Alert note

## Flag Information

- **Final Flag**: `flag{deepfake_identified_lsb_channel_revealed}`
- **Stego Password**: `ArtemisAI`

## Troubleshooting

### "steghide: command not found"
```bash
sudo apt-get install steghide
```

### "exiftool: command not found"
```bash
sudo apt-get install libimage-exiftool-perl
```

### Docker permission issues
```bash
sudo usermod -aG docker $USER
# Then log out and back in
```

### Port 8000 already in use
Edit `docker-compose.yml` and change `8000:8000` to `8001:8000` (or any other port)

## Next Steps

1. Review `README.md` for detailed documentation
2. Customize flags in `setup_challenge.py` if needed
3. Replace placeholder images with real ones for production
4. Upload `phantom_faces.zip` to your CTF platform

