# Phantom Faces CTF Challenge - Complete Summary

## Challenge Overview

**Name**: Phantom Faces — Evading AI Surveillance  
**Category**: AI/ML + Cybersecurity  
**Difficulty**: Easy–Medium  
**Flag Format**: `flag{...}`

## Complete File Structure

```
new-ai/
├── Dockerfile                 # Docker container definition
├── docker-compose.yml         # Docker Compose configuration
├── setup_challenge.py         # Challenge generation script
├── verify_challenge.py        # Verification script
├── package_challenge.sh       # Packaging script for CTFd
├── Makefile                   # Convenience commands
├── .dockerignore              # Docker ignore patterns
├── .gitignore                 # Git ignore patterns
├── README.md                  # Full documentation
├── QUICKSTART.md              # Quick start guide
├── CHALLENGE_SUMMARY.md       # This file
│
└── phantom_faces/             # Generated challenge files (created by setup)
    ├── faces/
    │   ├── staff_01.jpg       # Real image
    │   ├── staff_02.jpg       # Real image
    │   ├── staff_03.jpg       # Real image
    │   ├── staff_04.jpg       # Real image
    │   └── staff_05.jpg       # Deepfake (with metadata + stego)
    ├── recognition.log        # AI model prediction log
    ├── alert_note.txt         # Security alert with hints
    └── readme.txt             # Player-facing instructions
```

## Challenge Components

### 1. Staff Images (5 total)
- **4 Real Images**: `staff_01.jpg` through `staff_04.jpg`
  - High authenticity scores (96-99%)
  - Clean metadata from real cameras
  
- **1 Deepfake**: `staff_05.jpg`
  - Low authenticity score (53.2%)
  - Suspicious EXIF metadata
  - Contains steganographic content
  - GAN artifacts visible

### 2. Recognition Log (`recognition.log`)
- AI model predictions for all 5 images
- Clearly shows `staff_05.jpg` as suspicious
- Contains hints about metadata and password

### 3. Alert Note (`alert_note.txt`)
- Security alert from the facility
- Mentions LSB channel manipulation
- **Contains password hint**: "ArtemisAI"

### 4. Readme (`readme.txt`)
- Player-facing instructions
- Task list
- File inventory

## Solve Path

### Step 1: Initial Analysis
Player reads `readme.txt` and `recognition.log`
- Notices `staff_05.jpg` has low score (53.2%)
- Sees hint about metadata inconsistencies

### Step 2: Metadata Examination
```bash
exiftool staff_05.jpg
```
**Finds**:
- `Comment: flag_part1:deepfake_identified`
- `Software: FakeFaceGenX`
- `Artist: GAN_v2.1`
- `ImageDescription: AI Model Error: Low Authenticity`

**Extracts**: `flag_part1:deepfake_identified`

### Step 3: Steganography Extraction
Player reads `alert_note.txt` and finds password hint: "ArtemisAI"

```bash
steghide extract -sf staff_05.jpg -p ArtemisAI
```

**Extracts**: `hidden_msg.txt` containing `flag_part2:lsb_channel_revealed`

### Step 4: Flag Assembly
Combines both parts:
- Part 1: `deepfake_identified`
- Part 2: `lsb_channel_revealed`

**Final Flag**: `flag{deepfake_identified_lsb_channel_revealed}`

## Technical Details

### EXIF Metadata (Deepfake)
- **Comment**: `flag_part1:deepfake_identified`
- **Artist**: `GAN_v2.1`
- **Software**: `FakeFaceGenX`
- **ImageDescription**: `AI Model Error: Low Authenticity`

### Steganography
- **Tool**: steghide
- **Password**: `ArtemisAI`
- **Hidden Content**: `flag_part2:lsb_channel_revealed`
- **Embedded in**: `staff_05.jpg`

### Flag Parts
- **Part 1**: `deepfake_identified` (in EXIF Comment)
- **Part 2**: `lsb_channel_revealed` (in steganography)
- **Final**: `flag{deepfake_identified_lsb_channel_revealed}`

## Docker Setup

### Container Services
- **Base Image**: Ubuntu 22.04
- **Tools Installed**:
  - exiftool
  - steghide
  - imagemagick
  - python3
  - HTTP server

### Ports
- **Host**: 8000
- **Container**: 8000
- **Service**: HTTP file server

### Volumes
- Challenge files mounted for easy updates

## Setup Workflow

1. **Generate Files**: `python3 setup_challenge.py`
   - Creates directory structure
   - Generates images (or uses placeholders)
   - Adds EXIF metadata
   - Embeds steganography
   - Creates log files

2. **Build Docker**: `docker-compose build`
   - Installs dependencies
   - Sets up container environment

3. **Run Challenge**: `docker-compose up`
   - Starts HTTP server
   - Serves challenge files

4. **Package**: `make package`
   - Creates `phantom_faces.zip`
   - Ready for CTFd upload

## Customization

### Change Flag
Edit `setup_challenge.py`:
```python
FLAG_PART1 = "your_custom_part1"
FLAG_PART2 = "your_custom_part2"
```

### Change Password
Edit `setup_challenge.py`:
```python
STEGO_PASSWORD = "your_password"
```
Update `alert_note.txt` to hint at new password.

### Use Real Images
1. Download real face images from Unsplash/Pexels
2. Place in `phantom_faces/faces/` as `staff_01.jpg` through `staff_04.jpg`
3. Generate or obtain a deepfake for `staff_05.jpg`
4. Run setup script to add metadata and steganography

## CTFd Integration

### Challenge Settings
- **Name**: Phantom Faces — Evading AI Surveillance
- **Category**: AI/ML + Cybersecurity
- **Difficulty**: Easy–Medium
- **Points**: 300 (suggested)

### Description
Copy from `CTFD_DESCRIPTION.md` or use the description in `README.md`

### Files
Upload `phantom_faces.zip` (created by `make package`)

### Flag
`flag{deepfake_identified_lsb_channel_revealed}`

## Testing

### Verify Setup
```bash
make verify
```

### Test Solve Path
1. Extract zip file
2. Check recognition.log
3. Run exiftool on staff_05.jpg
4. Extract steganography with password
5. Verify flag assembly

## Notes

- Placeholder images are generated for quick setup
- For production, replace with real images
- Steghide requires the image to not already have embedded data
- All metadata is added using exiftool
- Challenge is fully self-contained in Docker

## Support Files

- **README.md**: Complete documentation
- **QUICKSTART.md**: Quick setup guide
- **Makefile**: Convenience commands
- **verify_challenge.py**: Setup verification
- **package_challenge.sh**: CTFd packaging

