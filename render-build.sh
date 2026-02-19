#!/bin/bash
# Build script for Render.com

set -e

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

echo "Running database migrations..."
python manage.py migrate

echo "Build complete!"
