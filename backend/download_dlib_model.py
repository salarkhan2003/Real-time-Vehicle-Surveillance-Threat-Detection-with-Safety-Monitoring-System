"""
Download dlib's 68-point facial landmark predictor
This is a high-accuracy trained model for precise eye detection
"""

import urllib.request
import bz2
import os

MODEL_URL = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
MODEL_FILE = "shape_predictor_68_face_landmarks.dat"
COMPRESSED_FILE = "shape_predictor_68_face_landmarks.dat.bz2"

def download_model():
    print("=" * 70)
    print("  DOWNLOADING HIGH-ACCURACY FACIAL LANDMARK MODEL")
    print("=" * 70)
    print(f"\nModel: dlib 68-point facial landmark predictor")
    print(f"Size: ~100MB")
    print(f"Accuracy: 95%+ for eye detection")
    print(f"Source: {MODEL_URL}")
    print("\nDownloading...")
    
    # Check if already exists
    if os.path.exists(MODEL_FILE):
        print(f"✅ Model already exists: {MODEL_FILE}")
        return
    
    # Download compressed file
    if not os.path.exists(COMPRESSED_FILE):
        print(f"Downloading {COMPRESSED_FILE}...")
        urllib.request.urlretrieve(MODEL_URL, COMPRESSED_FILE)
        print("✅ Download complete!")
    else:
        print(f"✅ Compressed file already exists: {COMPRESSED_FILE}")
    
    # Decompress
    print(f"\nDecompressing {COMPRESSED_FILE}...")
    with bz2.open(COMPRESSED_FILE, 'rb') as f_in:
        with open(MODEL_FILE, 'wb') as f_out:
            f_out.write(f_in.read())
    
    print(f"✅ Model extracted: {MODEL_FILE}")
    
    # Clean up compressed file
    if os.path.exists(COMPRESSED_FILE):
        os.remove(COMPRESSED_FILE)
        print(f"✅ Cleaned up: {COMPRESSED_FILE}")
    
    print("\n" + "=" * 70)
    print("  MODEL READY!")
    print("=" * 70)
    print(f"\n✅ {MODEL_FILE} is ready to use")
    print("   This model provides 68 facial landmarks for precise eye tracking")
    print("   Accuracy: 95%+ for eye open/closed detection")

if __name__ == "__main__":
    download_model()
