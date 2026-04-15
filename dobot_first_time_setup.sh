#!/bin/bash

echo "=== DoBot Environment Setup Starting ==="

# Step 1: Check if dialout group exists
if getent group dialout > /dev/null; then
    echo "dialout group exists."
else
    echo "WARNING: dialout group does not exist on this machine."
    echo "Please contact lab admin / IT to create it or grant serial device access."
fi

# Step 2: Check if current user is in dialout group
if id -nG "$USER" | grep -qw dialout; then
    echo "User $USER is already in dialout group."
else
    echo "User $USER is not in dialout group."
    echo "Attempting to add user to dialout group..."
    sudo usermod -aG dialout "$USER"
    if [ $? -eq 0 ]; then
        echo "User added to dialout group."
        echo "IMPORTANT: Fully log out of the computer and log back in."
    else
        echo "Could not add user to dialout group. You may need admin / IT help."
    fi
fi

# Step 3: Create virtual environment if needed
if [ ! -d "$HOME/dobot-venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$HOME/dobot-venv"
fi

# Step 4: Activate virtual environment
source "$HOME/dobot-venv/bin/activate"

# Step 5: Upgrade pip and install packages
echo "Installing Necessary Packages..."
pip install --upgrade pip
pip install google-genai opencv-python pyserial pydobot pupil-apriltags pygame

echo "Setup finished."
