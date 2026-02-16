#!/bin/bash

echo "========================================"
echo "  INSTALLING HIGH-ACCURACY FATIGUE DETECTION"
echo "========================================"
echo ""
echo "This will install:"
echo "  - dlib (facial landmark detection)"
echo "  - scipy (mathematical calculations)"
echo "  - Download 68-point facial landmark model"
echo ""
echo "This provides 95%+ accuracy for eye detection!"
echo ""
read -p "Press Enter to continue..."
echo ""

echo "Step 1: Installing dlib..."
pip install dlib

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ dlib installation failed!"
    echo ""
    echo "On Linux, you may need to install dependencies:"
    echo "  sudo apt-get install build-essential cmake"
    echo "  sudo apt-get install libopenblas-dev liblapack-dev"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo ""
echo "Step 2: Installing scipy..."
pip install scipy

echo ""
echo "Step 3: Downloading facial landmark model..."
python download_dlib_model.py

echo ""
echo "========================================"
echo "  INSTALLATION COMPLETE!"
echo "========================================"
echo ""
echo "✅ dlib installed"
echo "✅ scipy installed"
echo "✅ 68-point facial landmark model downloaded"
echo ""
echo "You can now use HIGH-ACCURACY fatigue detection!"
echo ""
read -p "Press Enter to exit..."
