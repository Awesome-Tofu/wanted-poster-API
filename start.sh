#!/bin/bash

# Install system dependencies
apt-get update && apt-get install -y libfreetype6-dev

# Install Python dependencies
pip install --no-cache-dir -r requirements.txt

# Set environment variables
export LD_LIBRARY_PATH=/usr/local/lib

# Run your application
uviron main:app --reload
