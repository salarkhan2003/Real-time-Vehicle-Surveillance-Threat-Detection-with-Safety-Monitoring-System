"""
Download YOLOv8 Medium model for high accuracy detection
"""

from ultralytics import YOLO
import os

print("=" * 70)
print("  Downloading YOLOv8 Medium Model for High Accuracy")
print("=" * 70)
print()
print("This will download YOLOv8m (~50MB)")
print("YOLOv8m provides much better accuracy than YOLOv8n")
print()
print("Accuracy comparison:")
print("  YOLOv8n (nano):   ~37% mAP - Fast but less accurate")
print("  YOLOv8m (medium): ~50% mAP - Much better accuracy")
print()
print("Downloading...")
print()

# Download YOLOv8m model
model = YOLO('yolov8m.pt')

print()
print("=" * 70)
print("  ✅ YOLOv8 Medium Model Downloaded Successfully!")
print("=" * 70)
print()
print("Model saved to: yolov8m.pt")
print()
print("The system will now use this high-accuracy model.")
print("Detection will be much better, especially for:")
print("  • Distant objects")
print("  • Small objects")
print("  • Objects moving closer")
print("  • Multiple objects")
print()
print("Next step: Start the server")
print("  python server.py")
print()
