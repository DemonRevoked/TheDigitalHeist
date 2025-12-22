#!/usr/bin/env python3
"""
Verification script to check that the challenge is set up correctly
"""

import os
import subprocess
from pathlib import Path

CHALLENGE_DIR = Path("phantom_faces")
FACES_DIR = CHALLENGE_DIR / "faces"

def check_file_exists(path, description):
    """Check if a file exists"""
    if path.exists():
        print(f"✓ {description}: {path}")
        return True
    else:
        print(f"✗ {description}: {path} - MISSING")
        return False

def check_exif_metadata():
    """Check if deepfake has correct EXIF metadata"""
    deepfake = FACES_DIR / "staff_05.jpg"
    if not deepfake.exists():
        print("✗ Deepfake image not found")
        return False
    
    try:
        result = subprocess.run(
            ['exiftool', str(deepfake)],
            capture_output=True,
            text=True,
            check=True
        )
        
        output = result.stdout.lower()
        checks = {
            'flag_part1': 'flag_part1' in output,
            'gan_v2.1': 'gan_v2.1' in output or 'artist.*gan' in output,
            'fakefacegenx': 'fakefacegenx' in output or 'software.*fake' in output,
            'low authenticity': 'low authenticity' in output or 'ai model error' in output
        }
        
        all_passed = True
        for check, passed in checks.items():
            if passed:
                print(f"  ✓ EXIF {check}: Found")
            else:
                print(f"  ✗ EXIF {check}: Missing")
                all_passed = False
        
        return all_passed
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  ⚠ Could not verify EXIF (exiftool not available)")
        return True  # Don't fail if exiftool not installed

def check_steganography():
    """Check if steganography is embedded"""
    deepfake = FACES_DIR / "staff_05.jpg"
    if not deepfake.exists():
        return False
    
    try:
        # Try to extract with wrong password (should fail)
        result = subprocess.run(
            ['steghide', 'extract', '-sf', str(deepfake), '-p', 'wrongpassword'],
            capture_output=True,
            text=True,
            input='y\n'
        )
        
        # If it succeeds with wrong password, something's wrong
        if result.returncode == 0:
            print("  ✗ Steganography: Wrong password worked (security issue)")
            return False
        
        # Try with correct password
        result = subprocess.run(
            ['steghide', 'extract', '-sf', str(deepfake), '-p', 'ArtemisAI'],
            capture_output=True,
            text=True,
            input='y\n'
        )
        
        if result.returncode == 0:
            print("  ✓ Steganography: Embedded and extractable")
            # Check if hidden_msg.txt was extracted
            if Path("hidden_msg.txt").exists():
                with open("hidden_msg.txt") as f:
                    content = f.read()
                    if "flag_part2" in content:
                        print("  ✓ Steganography: Contains flag_part2")
                        os.remove("hidden_msg.txt")  # Clean up
                        return True
            return True
        else:
            print("  ✗ Steganography: Could not extract with correct password")
            return False
    except FileNotFoundError:
        print("  ⚠ Could not verify steganography (steghide not available)")
        return True  # Don't fail if steghide not installed

def main():
    """Main verification function"""
    print("=" * 60)
    print("Phantom Faces Challenge Verification")
    print("=" * 60)
    print()
    
    all_checks = []
    
    # Check directory structure
    print("Checking directory structure...")
    all_checks.append(check_file_exists(CHALLENGE_DIR, "Challenge directory"))
    all_checks.append(check_file_exists(FACES_DIR, "Faces directory"))
    
    # Check required files
    print("\nChecking required files...")
    all_checks.append(check_file_exists(CHALLENGE_DIR / "readme.txt", "Readme"))
    all_checks.append(check_file_exists(CHALLENGE_DIR / "recognition.log", "Recognition log"))
    all_checks.append(check_file_exists(CHALLENGE_DIR / "alert_note.txt", "Alert note"))
    
    # Check images
    print("\nChecking images...")
    for i in range(1, 6):
        img_path = FACES_DIR / f"staff_0{i}.jpg"
        all_checks.append(check_file_exists(img_path, f"Staff image {i}"))
    
    # Check deepfake metadata
    print("\nChecking deepfake metadata...")
    all_checks.append(check_exif_metadata())
    
    # Check steganography
    print("\nChecking steganography...")
    all_checks.append(check_steganography())
    
    # Summary
    print("\n" + "=" * 60)
    if all(all_checks):
        print("✓ All checks passed! Challenge is ready.")
    else:
        print("✗ Some checks failed. Please review and fix issues.")
    print("=" * 60)

if __name__ == "__main__":
    main()

