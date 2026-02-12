"""
Download required models for fatigue detection
"""

import os
import urllib.request
import bz2
import shutil

def download_dlib_model():
    """Download dlib facial landmark model"""
    model_url = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
    model_file = "shape_predictor_68_face_landmarks.dat"
    compressed_file = model_file + ".bz2"
    
    if os.path.exists(model_file):
        print(f"✅ {model_file} already exists")
        return True
    
    print(f"📥 Downloading dlib facial landmark model...")
    print(f"   URL: {model_url}")
    print(f"   Size: ~99 MB (compressed)")
    
    try:
        # Download compressed file
        urllib.request.urlretrieve(model_url, compressed_file)
        print(f"✅ Downloaded {compressed_file}")
        
        # Decompress
        print(f"📦 Decompressing...")
        with bz2.BZ2File(compressed_file, 'rb') as f_in:
            with open(model_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Remove compressed file
        os.remove(compressed_file)
        print(f"✅ Model ready: {model_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        print(f"\n📝 Manual download instructions:")
        print(f"   1. Download: {model_url}")
        print(f"   2. Extract the .bz2 file")
        print(f"   3. Place {model_file} in the backend/ folder")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  Fatigue Detection Model Downloader")
    print("=" * 60)
    print()
    
    success = download_dlib_model()
    
    print()
    print("=" * 60)
    if success:
        print("✅ All models downloaded successfully!")
        print("   You can now run: python server.py")
    else:
        print("⚠️  Please download models manually")
    print("=" * 60)
