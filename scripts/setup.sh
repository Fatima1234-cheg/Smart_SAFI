#!/bin/bash

# SmartSafi - Smart City Management System
# Setup Script for Linux/Mac

set -e

echo "=================================="
echo "SmartSafi Setup Script"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python version: $PYTHON_VERSION"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip is not installed. Please install pip."
    exit 1
fi
echo "✅ pip is installed"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Removing..."
    rm -rf venv
fi

python3 -m venv venv
echo "✅ Virtual environment created"

# Activate virtual environment
echo ""
echo "🔄 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "📥 Installing requirements..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Requirements installed"
else
    echo "⚠️  requirements.txt not found"
fi

# Install development requirements
echo ""
read -p "🛠️  Install development dependencies? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "requirements-dev.txt" ]; then
        pip install -r requirements-dev.txt
        echo "✅ Development requirements installed"
    fi
fi

# Setup environment variables
echo ""
echo "🔧 Setting up environment variables..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env file created from .env.example"
        echo "⚠️  Please edit .env and update the configuration values"
    else
        echo "⚠️  .env.example not found"
    fi
else
    echo "⚠️  .env file already exists"
fi

# Create required directories
echo ""
echo "📁 Creating required directories..."
mkdir -p logs uploads backups instance
echo "✅ Directories created"

# Setup pre-commit hooks
echo ""
read -p "🔍 Setup pre-commit hooks? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f ".pre-commit-config.yaml" ]; then
        pip install pre-commit
        pre-commit install
        echo "✅ Pre-commit hooks installed"
    fi
fi

# Final message
echo ""
echo "=================================="
echo "✅ Setup completed successfully!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Ensure MongoDB is running"
echo "3. Ensure MQTT broker is running (optional)"
echo "4. Run: flask init-db"
echo "5. Run: flask create-admin"
echo "6. Start the server: python run.py"
echo ""
echo "Access the application at: http://localhost:5000"
echo ""

# Deactivate virtual environment
deactivate
