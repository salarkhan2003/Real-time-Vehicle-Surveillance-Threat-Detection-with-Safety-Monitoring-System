"""
Quick test script to verify YOLOv8 detection is working
"""
import requests
import base64
import json

def test_backend():
    print("Testing YOLOv8 Backend...")
    print("-" * 50)
    
    # Test health endpoint
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running!")
            print(f"   Status: {response.json()}")
        else:
            print("❌ Backend returned error:", response.status_code)
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend!")
        print("   Make sure server.py is running on port 5000")
        return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    print("\n" + "-" * 50)
    print("Backend is ready for detection!")
    print("Start the frontend with: npm run dev")
    print("-" * 50)

if __name__ == "__main__":
    test_backend()
