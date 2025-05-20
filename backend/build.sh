#!/bin/bash
# Railway build script

echo "Railway build script running"

# Make startup scripts executable
chmod +x railway_start.sh
chmod +x start.sh

# Ensure the necessary directories exist
mkdir -p static cache stats/history

echo "Railway build completed"
