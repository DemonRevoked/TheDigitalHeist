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

# Hardcoded encrypted value (pre-computed)
HARDCODED_ENCRYPTED_B64 = "U2FsdGVkX193RMHoyTF59LFTgNTfETmR4dO/sKGHaiEVgyGTcR8EpVVGFJzpMLVN"

# Dynamic challenge key - read from file or use default
def get_challenge_key():
    """Read challenge key from file if available"""
    key_file = os.environ.get('CHALLENGE_KEY_FILE', '/run/secrets/ai-01.key')
    if os.path.exists(key_file):
        try:
            with open(key_file, 'r') as f:
                key = f.read().strip()
                print(f"✓ Loaded challenge key from {key_file}")
                return key
        except Exception as e:
            print(f"Warning: Could not read challenge key file: {e}")
    print(f"✓ Using default challenge key (file not found: {key_file})")
    return "Dy5kVXHiKo9tQw4DB8XhCwCElS1pRg3NKdbYx0Be"

CHALLENGE_KEY = get_challenge_key()

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

def download_real_images():
    """
    Images are already copied in create_directories()
    This function is kept for compatibility
    """
    print(f"✓ Images ready in {ASSETS_DIR}/")

def add_challenge_key_to_img002():
    """Add dynamic challenge key metadata to img_002.png"""
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
        print("Warning: exiftool not found. Challenge key metadata will not be added.")
        return
    
    # Change to assets directory
    original_cwd = os.getcwd()
    os.chdir(ASSETS_DIR)
    
    try:
        # Add challenge key to EXIF metadata
        challenge_key_value = f"challenge_key:{CHALLENGE_KEY}"
        commands = [
            ['exiftool', '-Comment=', '-overwrite_original', 'img_002.png'],
            ['exiftool', f'-UserComment={challenge_key_value}', '-overwrite_original', 'img_002.png'],
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

def add_metadata_to_deepfake():
    """Add hardcoded encrypted metadata to the deepfake image (Part-1)"""
    deepfake_path = ASSETS_DIR / "img_005.png"
    
    if not deepfake_path.exists():
        print(f"Warning: {deepfake_path} not found")
        return
    
    # Check if exiftool is available
    try:
        subprocess.run(['exiftool', '-ver'], check=True, capture_output=True)
        exiftool_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        exiftool_available = False
        print("Warning: exiftool not found. Metadata will not be added.")
        return
    
    # Use hardcoded encrypted value
    enc_sig = f"enc_sig={HARDCODED_ENCRYPTED_B64}"
    
    # Change to assets directory
    original_cwd = os.getcwd()
    os.chdir(ASSETS_DIR)
    
    try:
        commands = [
            ['exiftool', '-Comment=', '-overwrite_original', 'img_005.png'],
            ['exiftool', '-UserComment=' + enc_sig, '-overwrite_original', 'img_005.png'],
            ['exiftool', '-Software=VisionPipeline_v3.4', '-overwrite_original', 'img_005.png'],
            ['exiftool', '-ImageDescription=Verification signature mismatch', '-overwrite_original', 'img_005.png'],
        ]
        
        for cmd in commands:
            try:
                subprocess.run(cmd, check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                print(f"Warning: Could not set metadata: {e}")
        
        # Cleanup exiftool backup file if it exists
        backup_file = Path("img_005.png_original")
        if backup_file.exists():
            backup_file.unlink()
        
        print(f"✓ Added encrypted metadata to img_005.png")
        
    except subprocess.CalledProcessError as e:
        print(f"Warning: Metadata addition failed: {e}")
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
        print(f"✓ Embedded LSB payload in img_005.png")
        
    except Exception as e:
        print(f"Warning: LSB embedding failed: {e}")

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
    
    # Important: Embed LSB FIRST, then add metadata
    # PIL save() strips EXIF, so metadata must be added after LSB embedding
    embed_steganography()
    add_metadata_to_deepfake()
    
    # Add challenge key to img_002
    add_challenge_key_to_img002()
    
    create_export_bin()
    create_telemetry_dump()
    create_cache_tmp()
    create_readme()
    
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
    print(f"Challenge Key: {CHALLENGE_KEY} (embedded in img_002.png)")
    print(f"Flag Part 1: [Encrypted in img_005.png metadata]")
    print(f"Flag Part 2: [LSB steganography in img_005.png]")
    print()
    print(f"Challenge files are in: {CHALLENGE_DIR}/")
    print(f"  - assets/img_001.png through img_005.png (images)")
    print(f"  - telemetry_dump.csv (feature export)")
    print(f"  - export_2024_11_19.bin (decision summary)")
    print(f"  - cache.tmp (system cache)")
    print(f"  - readme.txt (instructions)")
    print()
    print(f"Download package: incident_package.zip (ready for CTFd upload)")

if __name__ == "__main__":
    main()
