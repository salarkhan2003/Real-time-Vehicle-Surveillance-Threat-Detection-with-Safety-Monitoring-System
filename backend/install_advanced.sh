#!/bin/bash

echo "============================================================"
echo "  Installing Advanced Fatigue Detection System"
echo "============================================================"
echo ""

echo "Step 1: Installing Python dependencies..."
pip3 install flask flask-cors ultralytics opencv-python numpy Pillow scipy dlib imutils

echo ""
echo "Step 2: Downloading dlib facial landmark model..."
python3 download_models.py

echo ""
echo "============================================================"
echo "  Installation Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  1. Run: python3 server.py"
echo "  2. Start frontend in another terminal"
echo ""
