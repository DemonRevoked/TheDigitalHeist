# Phantom Faces — Evading AI Surveillance

A fully dockerized CTF challenge combining AI/ML and Cybersecurity forensics.

## Challenge Overview

**Difficulty**: Easy–Medium  
**Category**: AI/ML + Cybersecurity (Deepfake Forensics + Metadata Analysis + Steganography)  
**Flag Format**: `flag{...}`

### Storyline

The Artemis Complex deployed a new AI-powered security camera capable of real-time face classification using a Vision Transformer. Last night, the system flagged a critical anomaly: one staff photo is not a real human—it's an AI-generated deepfake planted by an insider attempting to bypass access controls.

Players must identify the deepfake and extract embedded intelligence using:
- EXIF metadata analysis
- GAN artifact detection
- Pixel pattern forensics
- LSB steganography
- AI model prediction logs

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed
- Python 3.8+ (for setup script)
- `exiftool` and `steghide` installed on host (for setup)

### Quick Start

1. **Generate Challenge Files**

   ```bash
   python3 setup_challenge.py
   ```

   This script will:
   - Create the challenge directory structure
   - Generate placeholder images (4 real, 1 deepfake)
   - Add suspicious EXIF metadata to the deepfake
   - Embed steganographic content in the deepfake
   - Create all log and documentation files

2. **Build Docker Image**

   ```bash
   docker-compose build
   ```

3. **Run Challenge**

   ```bash
   docker-compose up
   ```

   The challenge files will be served at `http://localhost:8000`

4. **Access Challenge Files**

   Players can download files from:
   - `http://localhost:8000/phantom_faces/faces/` - Staff images
   - `http://localhost:8000/phantom_faces/recognition.log` - AI log
   - `http://localhost:8000/phantom_faces/alert_note.txt` - Alert note
   - `http://localhost:8000/phantom_faces/readme.txt` - Challenge readme

### Manual Setup (Alternative)

If you prefer to set up manually or use real images:

1. **Prepare Real Images** (staff_01.jpg through staff_04.jpg)
   - Download from Unsplash/Pexels (CC0 license)
   - Ensure they are clean, real face photos
   - Save as JPG format

2. **Create Deepfake Image** (staff_05.jpg)
   - Generate using AI face generator (ThisPersonDoesNotExist, Stable Diffusion, etc.)
   - Add subtle GAN artifacts (irregular features, compression artifacts)
   - Save as JPG

3. **Add Metadata to Deepfake**

   ```bash
   exiftool -Comment="flag_part1:deepfake_identified" staff_05.jpg
   exiftool -Artist="GAN_v2.1" staff_05.jpg
   exiftool -Software="FakeFaceGenX" staff_05.jpg
   exiftool -ImageDescription="AI Model Error: Low Authenticity" staff_05.jpg
   ```

4. **Embed Steganography**

   Create `hidden_msg.txt`:
   ```
   flag_part2:lsb_channel_revealed
   ```

   Embed it:
   ```bash
   steghide embed -cf staff_05.jpg -ef hidden_msg.txt -p ArtemisAI
   ```

5. **Create Log Files**

   Copy the provided `recognition.log` and `alert_note.txt` to `phantom_faces/`

## Challenge Structure

```
phantom_faces/
├── faces/
│   ├── staff_01.jpg  (real)
│   ├── staff_02.jpg  (real)
│   ├── staff_03.jpg  (real)
│   ├── staff_04.jpg  (real)
│   └── staff_05.jpg  (deepfake with metadata + stego)
├── recognition.log
├── alert_note.txt
└── readme.txt
```

## Intended Solve Path

1. **Check Recognition Log**
   - Notice `staff_05.jpg` has low authenticity score (53.2%)
   - See hint about metadata inconsistencies

2. **Examine EXIF Metadata**
   ```bash
   exiftool staff_05.jpg
   ```
   - Find suspicious fields: `Software: FakeFaceGenX`, `Artist: GAN_v2.1`
   - Extract `Comment: flag_part1:deepfake_identified`

3. **Read Alert Note**
   - Find password hint: "Suspected insider codename: ArtemisAI"

4. **Extract Steganography**
   ```bash
   steghide extract -sf staff_05.jpg -p ArtemisAI
   ```
   - Extract `hidden_msg.txt` containing `flag_part2:lsb_channel_revealed`

5. **Assemble Final Flag**
   - Combine parts: `flag{deepfake_identified_lsb_channel_revealed}`

## Flag Information

- **Flag Part 1**: `deepfake_identified` (in EXIF Comment)
- **Flag Part 2**: `lsb_channel_revealed` (in steganography)
- **Final Flag**: `flag{deepfake_identified_lsb_channel_revealed}`
- **Stego Password**: `ArtemisAI` (hinted in alert_note.txt)

## CTFd Integration

1. Create a new challenge in CTFd
2. Set category: "AI/ML + Cybersecurity"
3. Set difficulty: "Easy–Medium"
4. Copy content from `CTFD_DESCRIPTION.md` as the challenge description
5. Upload `phantom_faces.zip` as challenge files
6. Set flag: `flag{deepfake_identified_lsb_channel_revealed}`

## Troubleshooting

### Steghide Issues

If `steghide` fails during setup:
- Ensure steghide is installed: `apt-get install steghide`
- You may need to embed steganography manually
- Alternative: Use `zsteg` for PNG format (requires converting to PNG)

### Image Generation

The setup script creates simple placeholder images. For production:
- Replace with real face images from Unsplash/Pexels
- Use actual AI-generated deepfakes for better realism
- Add more sophisticated GAN artifacts

### Docker Issues

If Docker build fails:
- Check that all dependencies are available
- Ensure `phantom_faces/` directory exists before building
- Run `setup_challenge.py` first to generate files

## Customization

### Changing the Flag

Edit `setup_challenge.py`:
```python
FLAG_PART1 = "your_part1"
FLAG_PART2 = "your_part2"
```

### Changing the Password

Edit `setup_challenge.py`:
```python
STEGO_PASSWORD = "your_password"
```

Update `alert_note.txt` to hint at the new password.

### Adding More Clues

- Modify `recognition.log` to add more hints
- Add additional EXIF fields with clues
- Include more files in the challenge bundle

## License

This CTF challenge is provided for educational purposes. Ensure you have proper licensing for any images used.

