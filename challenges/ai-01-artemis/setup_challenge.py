#!/usr/bin/env python3
"""
Setup script for Artemis Complex AI Verification Challenge
Generates all challenge files including images, metadata, and steganography
"""

import os
import subprocess
import shutil
from pathlib import Path
import random
import base64

# Try to import PIL, but make it optional
try:
    from PIL import Image, ImageDraw, ImageFilter
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Warning: PIL/Pillow not available. Will use ImageMagick or create simple placeholders.")

# Challenge configuration
CHALLENGE_DIR = Path("incident_package")
ASSETS_DIR = CHALLENGE_DIR / "assets"
FLAG_PART2 = "lsb_recovered"
FINAL_FLAG = f"flag{{deepfake_identified_{FLAG_PART2}}}"
STEGO_PASSWORD = "ArtemisAI"
CHALLENGE_KEY = "ARTEMIS_VERIFICATION_KEY_2024"

def create_directories():
    """Create incident_package directory structure with assets/"""
    source_faces = Path("faces")
    if not source_faces.exists():
        print(f"Error: {source_faces} directory not found!")
        print("Please create the faces/ directory with staff images.")
        return False
    
    # Create incident_package structure
    CHALLENGE_DIR.mkdir(exist_ok=True)
    ASSETS_DIR.mkdir(exist_ok=True)
    
    # Copy images from faces/ to assets/ with implicit indexing (img_001.png, etc.)
    print(f"✓ Creating {CHALLENGE_DIR} structure")
    for i in range(1, 6):
        for ext in ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']:
            source = source_faces / f"staff_0{i}{ext}"
            if source.exists():
                # Use img_001.png format (implicit indexing)
                dest = ASSETS_DIR / f"img_{i:03d}.png"
                if source.suffix.lower() != '.png':
                    # Convert to PNG if needed
                    if HAS_PIL:
                        try:
                            img = Image.open(source)
                            if img.mode == 'RGBA':
                                img.save(dest, 'PNG')
                            elif img.mode != 'RGB':
                                img = img.convert('RGB')
                                img.save(dest, 'PNG')
                            else:
                                img.save(dest, 'PNG')
                            print(f"✓ Converted {source.name} → {dest.name}")
                        except Exception as e:
                            print(f"Warning: Could not convert {source}: {e}")
                            shutil.copy(source, dest)
                    else:
                        shutil.copy(source, dest)
                else:
                    shutil.copy(source, dest)
                    print(f"✓ Copied {source.name} → {dest.name}")
                break
    return True

def create_minimal_jpeg(output_path, width, height):
    """Create a minimal valid JPEG file without PIL"""
    # This creates a very basic JPEG structure
    # For a real challenge, you should use proper images
    try:
        # Try ImageMagick first
        cmd = ['convert', '-size', f'{width}x{height}', 'xc:#e8d5c4', 
               '-quality', '95', str(output_path)]
        subprocess.run(cmd, check=True, capture_output=True)
        return
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Create a minimal JPEG header + simple data
    # This is a very basic approach - just creates a valid JPEG file
    jpeg_header = bytes([
        0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
        0x01, 0x01, 0x00, 0x48, 0x00, 0x48, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
        0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08, 0x07, 0x07, 0x07, 0x09,
        0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
        0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20,
        0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
        0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32,
        0x3C, 0x2E, 0x34, 0x34, 0x32, 0xFF, 0xC0, 0x00, 0x11, 0x08
    ])
    
    # Add dimensions (big-endian)
    height_bytes = height.to_bytes(2, 'big')
    width_bytes = width.to_bytes(2, 'big')
    
    # Minimal JPEG data (just enough to be valid)
    jpeg_data = jpeg_header + bytes([height_bytes[0], height_bytes[1], 
                                     width_bytes[0], width_bytes[1],
                                     0x03, 0x01, 0x22, 0x00, 0x02, 0x11, 0x01, 0x03, 0x11, 0x01,
                                     0xFF, 0xC4, 0x00, 0x1F, 0x00, 0x00, 0x01, 0x05, 0x01, 0x01,
                                     0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                     0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
                                     0x09, 0x0A, 0x0B, 0xFF, 0xC4, 0x00, 0xB5, 0x10, 0x00, 0x02,
                                     0x01, 0x03, 0x03, 0x02, 0x04, 0x03, 0x05, 0x05, 0x04, 0x04,
                                     0x00, 0x00, 0x01, 0x7D, 0x01, 0x02, 0x03, 0x00, 0x04, 0x11,
                                     0x05, 0x12, 0x21, 0x31, 0x41, 0x06, 0x13, 0x51, 0x61, 0x07,
                                     0x22, 0x71, 0x14, 0x32, 0x81, 0x91, 0xA1, 0x08, 0x23, 0x42,
                                     0xB1, 0xC1, 0x15, 0x52, 0xD1, 0xF0, 0x24, 0x33, 0x62, 0x72,
                                     0x82, 0x09, 0x0A, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x25, 0x26,
                                     0x27, 0x28, 0x29, 0x2A, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39,
                                     0x3A, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4A, 0x53,
                                     0x54, 0x55, 0x56, 0x57, 0x58, 0x59, 0x5A, 0x63, 0x64, 0x65,
                                     0x66, 0x67, 0x68, 0x69, 0x6A, 0x73, 0x74, 0x75, 0x76, 0x77,
                                     0x78, 0x79, 0x7A, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89,
                                     0x8A, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9A,
                                     0xA2, 0xA3, 0xA4, 0xA5, 0xA6, 0xA7, 0xA8, 0xA9, 0xAA, 0xB2,
                                     0xB3, 0xB4, 0xB5, 0xB6, 0xB7, 0xB8, 0xB9, 0xBA, 0xC2, 0xC3,
                                     0xC4, 0xC5, 0xC6, 0xC7, 0xC8, 0xC9, 0xCA, 0xD2, 0xD3, 0xD4,
                                     0xD5, 0xD6, 0xD7, 0xD8, 0xD9, 0xDA, 0xE1, 0xE2, 0xE3, 0xE4,
                                     0xE5, 0xE6, 0xE7, 0xE8, 0xE9, 0xEA, 0xF1, 0xF2, 0xF3, 0xF4,
                                     0xF5, 0xF6, 0xF7, 0xF8, 0xF9, 0xFA, 0xFF, 0xDA, 0x00, 0x0C,
                                     0x03, 0x01, 0x00, 0x02, 0x11, 0x03, 0x11, 0x00, 0x3F, 0x00])
    
    # Add some minimal image data (solid color)
    image_data = bytes([0xFF, 0xD9])  # JPEG end marker
    
    with open(output_path, 'wb') as f:
        f.write(jpeg_data + image_data)

def download_real_images():
    """
    Images are already copied in create_directories()
    This function is kept for compatibility
    """
    print(f"✓ Images ready in {ASSETS_DIR}/")

def add_metadata_to_deepfake():
    """Add AES-encrypted metadata to the deepfake image (Part-1)"""
    deepfake_path = ASSETS_DIR / "img_005.png"
    
    if not deepfake_path.exists():
        print(f"Warning: {deepfake_path} not found")
        return
    
    # Check if exiftool and openssl are available
    try:
        subprocess.run(['exiftool', '-ver'], check=True, capture_output=True)
        exiftool_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        exiftool_available = False
        print("Warning: exiftool not found. Metadata will not be added.")
        print("Install with: sudo apt-get install libimage-exiftool-perl")
        print("You will need to add metadata manually or run this script in the Docker container.")
        return
    
    try:
        subprocess.run(['openssl', 'version'], check=True, capture_output=True)
        openssl_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        openssl_available = False
        print("Warning: openssl not found. Encryption will not be performed.")
        print("Install with: sudo apt-get install openssl")
        print("You will need to encrypt metadata manually or run this script in the Docker container.")
        return
    
    # Part-1: AES-Encrypted Metadata
    plaintext = "deepfake_identified"
    encryption_key = "ARTEMIS-EMB-4"
    
    # Change to assets directory for temporary files
    original_cwd = os.getcwd()
    os.chdir(ASSETS_DIR)
    
    try:
        # Create plaintext file
        part1_txt = Path("part1.txt")
        with open(part1_txt, 'w') as f:
            f.write(plaintext)
        
        # Encrypt using AES-256-CBC
        part1_enc = Path("part1.enc")
        cmd = [
            'openssl', 'enc', '-aes-256-cbc', '-salt', '-pbkdf2',
            '-in', str(part1_txt),
            '-out', str(part1_enc),
            '-k', encryption_key
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Base64 encode
        with open(part1_enc, 'rb') as f:
            encrypted_data = f.read()
        part1_b64 = base64.b64encode(encrypted_data).decode('utf-8')
        
        # Add to EXIF UserComment - use = syntax to avoid exiftool treating value as filename
        enc_sig = f"enc_sig={part1_b64}"
        commands = [
            ['exiftool', '-Comment=', '-overwrite_original', 'img_005.png'],  # Remove any existing plaintext Comment
            ['exiftool', '-UserComment=' + enc_sig, '-overwrite_original', 'img_005.png'],
            ['exiftool', '-Software=VisionPipeline_v3.4', '-overwrite_original', 'img_005.png'],
            ['exiftool', '-ImageDescription=Verification signature mismatch', '-overwrite_original', 'img_005.png'],
        ]
        
        for cmd in commands:
            try:
                subprocess.run(cmd, check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                print(f"Warning: Could not set metadata: {e}")
        
        # Cleanup temporary files
        if part1_txt.exists():
            part1_txt.unlink()
        if part1_enc.exists():
            part1_enc.unlink()
        
        # Cleanup exiftool backup file if it exists
        backup_file = Path("img_005.png_original")
        if backup_file.exists():
            backup_file.unlink()
        
        print(f"✓ Added AES-encrypted metadata to deepfake")
        
    except subprocess.CalledProcessError as e:
        print(f"Warning: Encryption or metadata addition failed: {e}")
    finally:
        os.chdir(original_cwd)

def add_challenge_key_to_img002():
    """Add challenge key metadata to img_002.png"""
    img002_path = ASSETS_DIR / "img_002.png"
    
    if not img002_path.exists():
        print(f"Warning: {img002_path} not found")
        return
    
    # Check if exiftool is available
    try:
        subprocess.run(['exiftool', '-ver'], check=True, capture_output=True)
        exiftool_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        exiftool_available = False
        print("Warning: exiftool not found. Challenge key metadata will not be added to img_002.png.")
        print("Install with: sudo apt-get install libimage-exiftool-perl")
        return
    
    # Change to assets directory
    original_cwd = os.getcwd()
    os.chdir(ASSETS_DIR)
    
    try:
        # Add challenge key to EXIF metadata
        commands = [
            ['exiftool', '-Comment=', '-overwrite_original', 'img_002.png'],  # Remove any existing Comment
            ['exiftool', f'-UserComment=challenge_key:{CHALLENGE_KEY}', '-overwrite_original', 'img_002.png'],
            ['exiftool', '-Software=ArtemisVerify_v2.1', '-overwrite_original', 'img_002.png'],
            ['exiftool', '-ImageDescription=Verification sample - baseline reference', '-overwrite_original', 'img_002.png'],
        ]
        
        for cmd in commands:
            try:
                subprocess.run(cmd, check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                print(f"Warning: Could not set metadata on img_002.png: {e}")
        
        # Cleanup exiftool backup file if it exists
        backup_file = Path("img_002.png_original")
        if backup_file.exists():
            backup_file.unlink()
        
        print(f"✓ Added challenge key metadata to img_002.png")
        
    except subprocess.CalledProcessError as e:
        print(f"Warning: Metadata addition to img_002.png failed: {e}")
    finally:
        os.chdir(original_cwd)

def embed_steganography():
    """Embed LSB payload in deepfake using custom LSB script (Part-2)"""
    deepfake_path = ASSETS_DIR / "img_005.png"
    
    if not deepfake_path.exists():
        print(f"Warning: {deepfake_path} not found")
        return
    
    # Check if PIL is available
    if not HAS_PIL:
        print("Warning: PIL/Pillow not available. LSB steganography will not be embedded.")
        print("Install with: pip install pillow")
        print("You will need to embed steganography manually or run this script in the Docker container.")
        return
    
    try:
        from PIL import Image
        
        # Payload (ONLY this)
        message = f"flag_part2:{{{FLAG_PART2}}}<END>"
        bits = "".join(format(ord(c), "08b") for c in message)
        
        # Open image
        img = Image.open(deepfake_path).convert("RGB")
        pixels = img.load()
        
        width, height = img.size
        idx = 0
        bit_len = len(bits)
        
        # Embed bits into RGB LSBs
        for y in range(height):
            for x in range(width):
                if idx >= bit_len:
                    break
                
                r, g, b = pixels[x, y]
                rgb = [r, g, b]
                
                for i in range(3):
                    if idx < bit_len:
                        rgb[i] = (rgb[i] & ~1) | int(bits[idx])
                        idx += 1
                
                pixels[x, y] = tuple(rgb)
            
            if idx >= bit_len:
                break
        
        # Save image (overwrite)
        img.save(deepfake_path)
        print(f"✓ Embedded LSB payload in deepfake")
        
    except Exception as e:
        print(f"Warning: LSB embedding failed: {e}")
        print("You may need to embed steganography manually.")

def create_export_bin():
    """Create the model decision summary (semantic mislabeling - .bin but text)"""
    export_content = """=== Artemis Verification Pipeline Export ===
Timestamp: 2024-11-19T21:13:42Z
Module: EMBEDDING_VERIFIER
Build: v3.4.12

Active profile:
  profile_id      : ARTEMIS-EMB-4
  decision_mode   : strict
  threshold       : 0.35
  feature_space   : normalized

Batch execution summary:
  samples_processed : 5
  samples_accepted  : 3
  samples_rejected  : 2

Notes:
  Profile ARTEMIS-EMB-4 enforces tighter distribution bounds.
  Deviations beyond threshold result in immediate rejection.
  Multiple samples exceeded threshold. Investigation required to identify which contains intelligence artifacts.
"""
    
    export_path = CHALLENGE_DIR / "export_2024_11_19.bin"
    with open(export_path, 'w') as f:
        f.write(export_content)
    print(f"✓ Created export_2024_11_19.bin")

def create_telemetry_dump():
    """Create the telemetry dump CSV (AI feature export, implicit indexing)"""
    telemetry_content = """sample_id,blur_score,noise_variance,edge_entropy,embedding_distance
0,0.12,0.08,3.45,0.03
1,0.15,0.10,3.51,0.04
2,0.11,0.07,3.49,1.02
3,0.13,0.09,3.47,0.03
4,0.58,0.42,6.91,0.87
"""
    
    telemetry_path = CHALLENGE_DIR / "telemetry_dump.csv"
    with open(telemetry_path, 'w') as f:
        f.write(telemetry_content)
    print(f"✓ Created telemetry_dump.csv")

def create_cache_tmp():
    """Create noise file (decoy, adds realism)"""
    cache_content = """session_cache_init=true
last_clean_run=2024-11-18T23:01Z

active_profile=ARTEMIS-EMB-4
adaptive_blur_compensation=enabled
lighting_normalization=enabled
"""
    
    cache_path = CHALLENGE_DIR / "cache.tmp"
    with open(cache_path, 'w') as f:
        f.write(cache_content)
    print(f"✓ Created cache.tmp")

def create_readme():
    """Create the minimal, neutral readme (no spoilers)"""
    readme_content = """An incident package was recovered from an automated verification system.

One artifact triggered a rejection event.

Your task:
- Determine which artifact deviated from expected behavior
- Understand why the system rejected it
- Recover any intelligence associated with the incident

Flag format: flag{...}
"""
    
    readme_path = CHALLENGE_DIR / "readme.txt"
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    print(f"✓ Created readme.txt")

def create_zip_package():
    """Create the incident_package.zip file for download"""
    import zipfile
    import shutil
    
    zip_path = Path("incident_package.zip")
    
    print(f"  Checking for existing {zip_path}...")
    # Remove existing zip file or directory if it exists
    if zip_path.exists():
        if zip_path.is_dir():
            shutil.rmtree(zip_path)
            print(f"  Removed existing directory {zip_path}")
        else:
            zip_path.unlink()
            print(f"  Removed existing {zip_path}")
    
    # Verify that incident_package directory exists and has files
    print(f"  Verifying {CHALLENGE_DIR} exists...")
    if not CHALLENGE_DIR.exists():
        print(f"Error: {CHALLENGE_DIR} directory not found. Cannot create zip.")
        return False
    
    # Count files to be added
    print(f"  Collecting files from {CHALLENGE_DIR}...")
    files_to_add = list(CHALLENGE_DIR.rglob('*'))
    files_to_add = [f for f in files_to_add if f.is_file()]
    
    if not files_to_add:
        print(f"Error: No files found in {CHALLENGE_DIR}. Cannot create zip.")
        return False
    
    print(f"  Found {len(files_to_add)} files to add")
    
    # Create zip file
    print(f"  Creating zip file: {zip_path}")
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all files from incident_package directory
            # Maintain directory structure: incident_package/ should be root in zip
            for file_path in files_to_add:
                # Get relative path from incident_package directory
                # This ensures incident_package/ is the root in the zip
                arcname = file_path.relative_to(CHALLENGE_DIR.parent)
                zipf.write(file_path, arcname)
        
        # Verify zip was created correctly (must be a file, not a directory)
        if zip_path.exists() and zip_path.is_file():
            zip_size = zip_path.stat().st_size
            zip_size_mb = zip_size / (1024 * 1024)
            print(f"✓ Created {zip_path} for download ({zip_size_mb:.2f} MB)")
            print(f"  Added {len(files_to_add)} files to zip")
            return True
        else:
            print(f"Error: {zip_path} was not created as a file (may be a directory)")
            if zip_path.exists() and zip_path.is_dir():
                shutil.rmtree(zip_path)
            return False
            
    except Exception as e:
        print(f"Error creating zip file: {e}")
        import traceback
        traceback.print_exc()
        # Clean up if something went wrong
        if zip_path.exists():
            if zip_path.is_dir():
                shutil.rmtree(zip_path)
            else:
                zip_path.unlink()
        return False

def create_ctfd_description():
    """Create CTFd challenge description file"""
    description = """# Artemis Complex — AI Verification Anomaly

## Challenge Information
- **Category**: AI/ML + Cybersecurity
- **Difficulty**: Medium
- **Points**: 400

## Description

An incident package was recovered from an automated verification system.

One artifact triggered a rejection event.

Your task:
- Determine which artifact deviated from expected behavior
- Understand why the system rejected it
- Recover any intelligence associated with the incident

**Flag format**: `flag{...}`

## Files

Download the challenge files and begin your investigation.

This challenge requires reasoning about system outputs and identifying anomalies.
"""
    
    desc_path = Path("CTFD_DESCRIPTION.md")
    with open(desc_path, 'w') as f:
        f.write(description)
    print(f"✓ Created CTFD_DESCRIPTION.md")

def main():
    """Main setup function"""
    print("=" * 60)
    print("Artemis Complex AI Verification Challenge Setup")
    print("=" * 60)
    print()
    
    if not create_directories():
        print("Setup failed: faces directory not found")
        return
    
    download_real_images()
    add_metadata_to_deepfake()
    add_challenge_key_to_img002()
    embed_steganography()
    create_export_bin()
    create_telemetry_dump()
    create_cache_tmp()
    create_readme()
    create_ctfd_description()
    
    # Create zip package (must be last, after all files are created)
    print()
    print("Creating download package...")
    try:
        create_zip_package()
    except Exception as e:
        print(f"Error during zip creation: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print(f"Final Flag: {FINAL_FLAG}")
    print(f"Stego Password: {STEGO_PASSWORD}")
    print(f"Challenge Key: {CHALLENGE_KEY} (embedded in img_002.png metadata)")
    print()
    print(f"Challenge files are in: {CHALLENGE_DIR}/")
    print(f"  - assets/img_001.png through img_005.png (images)")
    print(f"  - telemetry_dump.csv (feature export)")
    print(f"  - export_2024_11_19.bin (decision summary)")
    print(f"  - cache.tmp (system cache)")
    print(f"  - readme.txt (instructions)")
    print()
    print(f"Download package: incident_package.zip (ready for CTFd upload)")
    print()
    
    # Check if we're missing tools
    missing_tools = []
    try:
        subprocess.run(['exiftool', '-ver'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing_tools.append('exiftool')
    
    try:
        subprocess.run(['openssl', 'version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing_tools.append('openssl')
    
    if not HAS_PIL:
        missing_tools.append('pillow')
    
    if missing_tools:
        print("⚠ NOTE: Some tools are missing. For complete setup:")
        print("  1. Build Docker image (has all tools):")
        print("     docker-compose build")
        print()
        print("  2. Run setup inside Docker container (recommended):")
        print("     docker-compose run --rm phantom-faces python3 /challenge/setup_challenge.py")
        print("     OR use: make setup-docker")
        print()
        print("  OR install tools locally:")
        for tool in missing_tools:
            if tool == 'exiftool':
                print("     sudo apt-get install libimage-exiftool-perl")
            elif tool == 'openssl':
                print("     sudo apt-get install openssl")
            elif tool == 'pillow':
                print("     pip install pillow")
        print()
    
    print("To build Docker image:")
    print("  docker-compose build")
    print()
    print("To run challenge:")
    print("  docker-compose up")
    print()
    print("Challenge will be available at: http://localhost:8000")

if __name__ == "__main__":
    main()

