#!/bin/bash
# Setup script for Match-3 Bot

echo "Setting up Match-3 Game Bot..."
echo

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create virtual environment
echo
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo
echo "Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

echo
echo "Setup complete!"
echo
echo "To use the bot:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Make sure you have ChromeDriver or GeckoDriver installed"
echo "3. Run the bot: python match3_bot.py <game-url>"
echo
echo "For more information, see README.md"
