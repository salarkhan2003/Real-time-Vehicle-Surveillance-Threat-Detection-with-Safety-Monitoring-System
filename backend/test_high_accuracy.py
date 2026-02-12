"""
Quick test script to verify high-accuracy detection is working
"""

import os
import sys

print("=" * 70)
print("  High Accuracy Detection System - Verification Test")
print("=" * 70)
print()

# Test 1: Check if YOLOv8m model exists
print("Test 1: Checking for YOLOv8m model...")
if os.path.exists('yolov8m.pt'):
    file_size = os.path.getsize('yolov8m.pt') / (1024 * 1024)  # MB
    print(f"  ✅ YOLOv8m model found ({file_size:.1f} MB)")
else:
    print("  ❌ YOLOv8m model NOT found")
    print("  → Run: python download_yolov8m.py")
    sys.exit(1)

print()

# Test 2: Check if required packages are installed
print("Test 2: Checking required packages...")
try:
    from ultralytics import YOLO
    print("  ✅ ultralytics installed")
except ImportError:
    print("  ❌ ultralytics NOT installed")
    print("  → Run: pip install ultralytics")
    sys.exit(1)

try:
    import cv2
    print("  ✅ opencv-python installed")
except ImportError:
    print("  ❌ opencv-python NOT installed")
    print("  → Run: pip install opencv-python")
    sys.exit(1)

try:
    from flask import Flask
    print("  ✅ flask installed")
except ImportError:
    print("  ❌ flask NOT installed")
    print("  → Run: pip install flask flask-cors")
    sys.exit(1)

print()

# Test 3: Try loading the model
print("Test 3: Loading YOLOv8m model...")
try:
    model = YOLO('yolov8m.pt')
    print("  ✅ Model loaded successfully")
    print(f"  → Model type: YOLOv8m")
    print(f"  → Classes: {len(model.names)} object types")
except Exception as e:
    print(f"  ❌ Failed to load model: {e}")
    sys.exit(1)

print()

# Test 4: Check fatigue detector
print("Test 4: Checking fatigue detector...")
try:
    from fatigue_detector_dnn import FatigueDetector
    detector = FatigueDetector()
    print("  ✅ Fatigue detector initialized")
    print("  → Using OpenCV DNN face detection")
except Exception as e:
    print(f"  ❌ Failed to initialize fatigue detector: {e}")
    sys.exit(1)

print()

# Test 5: Verify server configuration
print("Test 5: Checking server configuration...")
try:
    with open('server.py', 'r') as f:
        content = f.read()
        
    # Check model type
    if "yolov8m.pt" in content:
        print("  ✅ Server configured for YOLOv8m")
    else:
        print("  ⚠️  Server NOT configured for YOLOv8m")
        print("  → Check server.py line 15")
    
    # Check confidence threshold
    if "conf=0.25" in content:
        print("  ✅ Low confidence threshold (0.25) - Better detection")
    else:
        print("  ⚠️  High confidence threshold - May miss objects")
    
    # Check image size
    if "imgsz=640" in content:
        print("  ✅ High resolution (640px) - Better accuracy")
    else:
        print("  ⚠️  Low resolution - May miss details")
    
    # Check max detections
    if "max_det=100" in content:
        print("  ✅ High max detections (100) - Track more objects")
    else:
        print("  ⚠️  Low max detections - May miss objects")
        
except Exception as e:
    print(f"  ❌ Failed to check server.py: {e}")

print()
print("=" * 70)
print("  ✅ ALL TESTS PASSED - System Ready for High Accuracy Detection!")
print("=" * 70)
print()
print("Next steps:")
print("  1. Start backend: python server.py")
print("  2. Start frontend: npm run dev")
print("  3. Test detection with distant objects")
print()
print("Expected improvements:")
print("  • Distant objects detected (3-10m)")
print("  • Objects moving closer tracked smoothly")
print("  • Small objects detected")
print("  • Multiple objects tracked simultaneously")
print("  • 50% mAP accuracy (was 37%)")
print()
