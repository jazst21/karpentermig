#!/bin/bash

set -e

# Navigate to the project root directory
cd "$(dirname "$0")"

# Ensure we have the latest setuptools, wheel, and twine
pip install --upgrade setuptools wheel twine

# Check if setup.py exists
if [ ! -f setup.py ]; then
    echo "Error: setup.py not found in the project root directory."
    exit 1
fi

# Check if README.md exists
if [ ! -f README.md ]; then
    echo "Warning: README.md not found in the project root directory."
fi

# Clean up any old distribution files
rm -rf dist build *.egg-info

# Build the package
python setup.py sdist bdist_wheel

# Check if the build was successful
if [ $? -eq 0 ]; then
    echo "Package built successfully. Distribution files are in the 'dist' directory."
    
    # Optional: Check the distribution
    echo "Checking the distribution..."
    twine check dist/*
    
    # If everything is successful, remove old dist folder contents
    echo "Removing old distribution files..."
    find dist -type f ! -name "*.whl" ! -name "*.tar.gz" -delete
    
    # Install the newly built package
    echo "Installing the newly built package..."
    pip install dist/*.whl --force-reinstall
    
    echo "Build process completed successfully and package installed."
else
    echo "Build process failed."
    exit 1
fi