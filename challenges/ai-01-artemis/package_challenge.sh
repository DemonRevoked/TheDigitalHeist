#!/bin/bash
# Package the challenge for CTFd submission

echo "Packaging Phantom Faces challenge..."

# Create zip file with incident_package directory
cd incident_package
zip -r ../incident_package.zip .
cd ..

echo "✓ Created incident_package.zip"
echo ""
echo "This file can be uploaded to CTFd as the challenge download."

