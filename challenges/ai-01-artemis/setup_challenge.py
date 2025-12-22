#!/usr/bin/env python3
"""
Setup script for Phantom Faces CTF Challenge
Generates all challenge files including images, metadata, and steganography
"""

import os
import subprocess
import shutil
from pathlib import Path
import random

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
    """Add subtle EXIF metadata to the deepfake image (no flag hints)"""
    deepfake_path = ASSETS_DIR / "img_005.png"
    
    if not deepfake_path.exists():
        print(f"Warning: {deepfake_path} not found")
        return
    
    if not deepfake_path.exists():
        print(f"Error: {deepfake_path} not found")
        return
    
    # Check if exiftool is available
    try:
        subprocess.run(['exiftool', '-ver'], check=True, capture_output=True)
        exiftool_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        exiftool_available = False
        print("Warning: exiftool not found. Metadata will not be added.")
        print("Install with: sudo apt-get install libimage-exiftool-perl")
        print("You will need to add metadata manually or run this script in the Docker container.")
        return
    
    # Add subtle metadata (no flag hints, just supports AI suspicion)
    commands = [
        ['exiftool', '-Software', 'VisionPipeline_v3.4', '-overwrite_original', str(deepfake_path)],
        ['exiftool', '-ImageDescription', 'Embedding anomaly detected', '-overwrite_original', str(deepfake_path)],
    ]
    
    for cmd in commands:
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not set metadata: {e}")
    
    print(f"✓ Added suspicious metadata to deepfake")

def create_stego_file():
    """Create the hidden message file for steganography (only part 2)"""
    hidden_msg = f"flag_part2:{FLAG_PART2}\n"
    hidden_file = Path("hidden_msg.txt")
    
    with open(hidden_file, 'w') as f:
        f.write(hidden_msg)
    
    print(f"✓ Created hidden message file")
    return hidden_file

def embed_steganography():
    """Embed hidden message in deepfake using steghide (LSB for PNG)"""
    deepfake_path = ASSETS_DIR / "img_005.png"
    hidden_file = create_stego_file()
    
    if not deepfake_path.exists():
        print(f"Warning: {deepfake_path} not found")
        if 'hidden_file' in locals() and hidden_file.exists():
            hidden_file.unlink()
        return
    hidden_file = create_stego_file()
    
    if not deepfake_path.exists():
        print(f"Error: {deepfake_path} not found")
        if hidden_file.exists():
            hidden_file.unlink()
        return
    
    # Check if steghide is available
    try:
        subprocess.run(['steghide', '--version'], check=True, capture_output=True)
        steghide_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        steghide_available = False
        print("Warning: steghide not found. Steganography will not be embedded.")
        print("Install with: sudo apt-get install steghide")
        print("You will need to embed steganography manually or run this script in the Docker container.")
        if hidden_file.exists():
            hidden_file.unlink()
        return
    
    # Create a temporary copy for steghide (steghide needs to overwrite)
    temp_path = ASSETS_DIR / "img_005_temp.png"
    shutil.copy(deepfake_path, temp_path)
    
    try:
        # Embed using steghide
        cmd = [
            'steghide', 'embed',
            '-cf', str(temp_path),
            '-ef', str(hidden_file),
            '-p', STEGO_PASSWORD,
            '-f'  # Force overwrite
        ]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, input='y\n')
        
        # Replace original with stego version
        shutil.move(temp_path, deepfake_path)
        print(f"✓ Embedded steganography in deepfake")
    except subprocess.CalledProcessError as e:
        print(f"Warning: Steghide embedding failed: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr.decode() if isinstance(e.stderr, bytes) else e.stderr}")
        print("Note: The image may already have embedded data, or there was an error.")
        print("You may need to embed steganography manually.")
        if temp_path.exists():
            # Restore original if embedding failed
            shutil.move(temp_path, deepfake_path)
    except FileNotFoundError:
        print("Warning: steghide not found. Install with: apt-get install steghide")
        print("You may need to embed steganography manually.")
        if temp_path.exists():
            shutil.move(temp_path, deepfake_path)
    
    # Clean up
    if hidden_file.exists():
        hidden_file.unlink()

def create_export_bin():
    """Create the model decision summary (semantic mislabeling - .bin but text)"""
    export_content = """Batch verification summary:
Samples processed: 5
Acceptance threshold: 0.35

Result:
Sample[4] exceeded deviation limits.

Action:
Sample rejected.
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
2,0.11,0.07,3.49,0.02
3,0.13,0.09,3.47,0.03
4,0.58,0.42,6.91,0.87
"""
    
    telemetry_path = CHALLENGE_DIR / "telemetry_dump.csv"
    with open(telemetry_path, 'w') as f:
        f.write(telemetry_content)
    print(f"✓ Created telemetry_dump.csv")

def create_cache_tmp():
    """Create noise file (decoy, adds realism)"""
    cache_content = """session_id=8842
prev_run_status=clean
lighting_variance_check=ok
blur_threshold_adjusted=true
"""
    
    cache_path = CHALLENGE_DIR / "cache.tmp"
    with open(cache_path, 'w') as f:
        f.write(cache_content)
    print(f"✓ Created cache.tmp")

def create_readme():
    """Create the minimal, neutral readme (no spoilers)"""
    readme_content = """An incident package was recovered from an automated verification system.

One artifact in this package triggered a rejection event.

Your task:
- Determine which artifact caused the rejection
- Understand why it deviated from expected behavior
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
    
    zip_path = Path("incident_package.zip")
    
    # Remove existing zip if it exists
    if zip_path.exists():
        zip_path.unlink()
    
    # Create zip file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add all files from incident_package directory
        for file_path in CHALLENGE_DIR.rglob('*'):
            if file_path.is_file():
                # Get relative path for zip (maintain directory structure)
                arcname = file_path.relative_to(CHALLENGE_DIR.parent)
                zipf.write(file_path, arcname)
    
    print(f"✓ Created {zip_path} for download")

def create_ctfd_description():
    """Create CTFd challenge description file"""
    description = """# Phantom Faces — Evading AI Surveillance

## Challenge Information
- **Category**: AI/ML + Cybersecurity
- **Difficulty**: Medium
- **Points**: 400

## Description

An incident package was recovered from an automated verification system.

One artifact in this package triggered a rejection event.

Your task:
- Determine which artifact caused the rejection
- Understand why it deviated from expected behavior
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
    print("Phantom Faces CTF Challenge Setup")
    print("=" * 60)
    print()
    
    if not create_directories():
        print("Setup failed: faces directory not found")
        return
    
    download_real_images()
    add_metadata_to_deepfake()
    embed_steganography()
    create_export_bin()
    create_telemetry_dump()
    create_cache_tmp()
    create_readme()
    create_ctfd_description()
    create_zip_package()
    
    print()
    print("=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print(f"Final Flag: {FINAL_FLAG}")
    print(f"Stego Password: {STEGO_PASSWORD}")
    print()
    print(f"Challenge files are in: {CHALLENGE_DIR}/")
    print(f"  - assets/img_001.png through img_005.png (images)")
    print(f"  - telemetry_dump.csv (feature export)")
    print(f"  - export_2024_11_19.bin (decision summary)")
    print(f"  - cache.tmp (system cache)")
    print(f"  - readme.txt (instructions)")
    print()
    
    # Check if we're missing tools
    missing_tools = []
    try:
        subprocess.run(['exiftool', '-ver'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing_tools.append('exiftool')
    
    try:
        subprocess.run(['steghide', '--version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing_tools.append('steghide')
    
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
            elif tool == 'steghide':
                print("     sudo apt-get install steghide")
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

