#!/bin/bash
# Add local bin directory to PATH to quiet pip warning
export PATH="$HOME/.local/bin:$PATH"

# Install requirements.txt if it exists in the current working directory
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install --user -r requirements.txt
    echo "Dependencies installed successfully."
else
    echo "No requirements.txt found in working directory, skipping dependency installation."
fi
