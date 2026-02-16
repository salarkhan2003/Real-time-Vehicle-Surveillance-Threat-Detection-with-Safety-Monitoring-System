"""
Download YOLOv10-X model for maximum accuracy surveillance
YOLOv10-X is the largest and most accurate YOLOv10 model
"""

import os
import urllib.request
from tqdm import tqdm

class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

def download_yolov10x():
    """Download YOLOv10-X model"""
    
    print("=" * 70)
    print("  DOWNLOADING YOLOv10-X - MAXIMUM ACCURACY SURVEILLANCE MODEL")
    print("=" * 70)
    print("\nModel: YOLOv10-X (Extra Large)")
    print("Size: ~140MB")
    print("Accuracy: 56.8% mAP (highest in YOLOv10 series)")
    print("Speed: 30+ FPS (real-time)")
    print("\nThis is the BEST YOLOv10 model for surveillance!")
    print()
    
    model_url = "https://github.com/THU-MIG/yolov10/releases/download/v1.1/yolov10x.pt"
    model_file = "yolov10x.pt"
    
    # Check if already exists
    if os.path.exists(model_file):
        print(f"✅ Model already exists: {model_file}")
        print(f"   Size: {os.path.getsize(model_file) / (1024*1024):.1f} MB")
        return
    
    # Download
    print(f"Downloading from: {model_url}")
    print(f"Saving to: {model_file}")
    print()
    
    try:
        with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=model_file) as t:
            urllib.request.urlretrieve(model_url, filename=model_file, reporthook=t.update_to)
        
        print()
        print("=" * 70)
        print("  DOWNLOAD COMPLETE!")
        print("=" * 70)
        print(f"\n✅ {model_file} downloaded successfully")
        print(f"   Size: {os.path.getsize(model_file) / (1024*1024):.1f} MB")
        print("\nYOLOv10-X is ready for maximum accuracy surveillance!")
        
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        print("\nAlternative: Download manually from:")
        print(model_url)
        print(f"Save as: {model_file}")

if __name__ == "__main__":
    download_yolov10x()
