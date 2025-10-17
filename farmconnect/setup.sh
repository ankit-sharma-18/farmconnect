#!/bin/bash

# FarmConnect Setup Script

echo "Setting up FarmConnect..."

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Make migrations
python manage.py makemigrations accounts products orders reviews
python manage.py migrate

# Create superuser
echo "Creating superuser..."
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

echo "Setup complete! Run 'python manage.py runserver' to start the application."