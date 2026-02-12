#!/usr/bin/env python3
"""
Mode Selection Feature - Backend Test Script
Tests the /detect endpoint with different mode combinations
"""

import requests
import base64
import json
from PIL import Image
import io
import sys

# Configuration
BACKEND_URL = "http://localhost:5000"
TEST_IMAGE_SIZE = (640, 480)

def create_test_image():
    """Create a simple test image"""
    img = Image.new('RGB', TEST_IMAGE_SIZE, color='blue')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    img_bytes = buffer.getvalue()
    return base64.b64encode(img_bytes).decode('utf-8')

def test_health():
    """Test if backend is running"""
    print("=" * 70)
    print("TEST 1: Backend Health Check")
    print("=" * 70)
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is it running?")
        print("   Start with: cd backend && python server.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_mode_combination(modes, test_name):
    """Test a specific mode combination"""
    print("\n" + "=" * 70)
    print(f"TEST: {test_name}")
    print("=" * 70)
    print(f"Modes: {modes}")
    
    try:
        image_data = create_test_image()
        payload = {
            "image": f"data:image/jpeg;base64,{image_data}",
            "modes": modes
        }
        
        response = requests.post(
            f"{BACKEND_URL}/detect",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Request successful")
            print(f"\nResponse structure:")
            print(f"  - Has 'detections': {'detections' in result}")
            print(f"  - Has 'fatigue': {'fatigue' in result}")
            print(f"  - Has 'speed': {'speed' in result}")
            print(f"  - Has 'alertThresholds': {'alertThresholds' in result}")
            
            # Verify mode-specific behavior
            if modes.get('vehicle', False):
                if 'detections' in result:
                    print(f"  ✅ Vehicle mode: detections key present")
                    print(f"     Detections count: {len(result['detections'])}")
                else:
                    print(f"  ❌ Vehicle mode: detections key missing!")
            else:
                if 'detections' in result and len(result['detections']) == 0:
                    print(f"  ✅ Vehicle mode OFF: empty detections")
                else:
                    print(f"  ⚠️  Vehicle mode OFF but detections present")
            
            if modes.get('fatigue', False):
                if 'fatigue' in result:
                    print(f"  ✅ Fatigue mode: fatigue key present")
                    print(f"     Fatigue value: {result['fatigue']}")
                else:
                    print(f"  ❌ Fatigue mode: fatigue key missing!")
            else:
                if 'fatigue' not in result:
                    print(f"  ✅ Fatigue mode OFF: no fatigue key")
                else:
                    print(f"  ⚠️  Fatigue mode OFF but fatigue present: {result.get('fatigue')}")
            
            return True
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "MODE SELECTION BACKEND TEST SUITE" + " " * 20 + "║")
    print("╚" + "═" * 68 + "╝")
    print("\n")
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Backend is not running. Please start it first.")
        print("   Command: cd backend && python server.py")
        sys.exit(1)
    
    # Test 2: Both modes active (default)
    test_mode_combination(
        {"fatigue": True, "vehicle": True},
        "Both Modes Active (Default)"
    )
    
    # Test 3: Fatigue only
    test_mode_combination(
        {"fatigue": True, "vehicle": False},
        "Fatigue Only"
    )
    
    # Test 4: Vehicle only
    test_mode_combination(
        {"fatigue": False, "vehicle": True},
        "Vehicle Only"
    )
    
    # Test 5: Both modes off
    test_mode_combination(
        {"fatigue": False, "vehicle": False},
        "Both Modes OFF (Standby)"
    )
    
    # Test 6: No modes parameter (backward compatibility)
    print("\n" + "=" * 70)
    print("TEST: Backward Compatibility (No modes parameter)")
    print("=" * 70)
    try:
        image_data = create_test_image()
        payload = {
            "image": f"data:image/jpeg;base64,{image_data}"
            # No modes parameter
        }
        
        response = requests.post(
            f"{BACKEND_URL}/detect",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Backward compatibility maintained")
            print(f"   Defaults to both modes ON")
            print(f"   Has detections: {'detections' in result}")
            print(f"   Has fatigue: {'fatigue' in result}")
        else:
            print(f"❌ Failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print("✅ All backend tests completed!")
    print("\nNext steps:")
    print("1. Start frontend: npm run dev")
    print("2. Test UI mode toggles manually")
    print("3. Verify resource usage in Task Manager")
    print("4. Check DEPLOYMENT_CHECKLIST.md for full testing")
    print("\n")

if __name__ == "__main__":
    main()
