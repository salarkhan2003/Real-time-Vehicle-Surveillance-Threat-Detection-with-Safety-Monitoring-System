#!/usr/bin/env python3
"""
Test script to verify fatigue detection accuracy
"""

import cv2
import numpy as np
from fatigue_detector_advanced import FatigueDetector
import time

def create_test_image_with_face(eyes_open=True):
    """Create a simple test image"""
    # Create blank image
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    img[:] = (200, 200, 200)  # Gray background
    
    # Draw a simple face (circle)
    cv2.circle(img, (320, 240), 100, (180, 150, 120), -1)
    
    if eyes_open:
        # Draw open eyes
        cv2.circle(img, (280, 220), 15, (255, 255, 255), -1)  # Left eye white
        cv2.circle(img, (360, 220), 15, (255, 255, 255), -1)  # Right eye white
        cv2.circle(img, (280, 220), 8, (0, 0, 0), -1)  # Left pupil
        cv2.circle(img, (360, 220), 8, (0, 0, 0), -1)  # Right pupil
    else:
        # Draw closed eyes (lines)
        cv2.line(img, (265, 220), (295, 220), (0, 0, 0), 3)
        cv2.line(img, (345, 220), (375, 220), (0, 0, 0), 3)
    
    return img

def test_fatigue_detector():
    """Test the fatigue detector with different scenarios"""
    print("=" * 70)
    print("  FATIGUE DETECTION ACCURACY TEST")
    print("=" * 70)
    print()
    
    # Initialize detector
    print("Initializing detector...")
    detector = FatigueDetector()
    print()
    
    # Test 1: Eyes Open (Should be LOW fatigue)
    print("TEST 1: Eyes Open (Alert State)")
    print("-" * 70)
    img_open = create_test_image_with_face(eyes_open=True)
    
    # Run detection multiple times to test temporal smoothing
    scores = []
    for i in range(5):
        score, details = detector.detect(img_open)
        scores.append(score)
        print(f"  Frame {i+1}: Fatigue = {score:.2f} ({score*100:.0f}%) - {details['status']}")
        time.sleep(0.1)
    
    avg_score = np.mean(scores)
    print(f"\n  Average: {avg_score:.2f} ({avg_score*100:.0f}%)")
    
    if avg_score < 0.3:
        print("  ✅ PASS: Low fatigue detected for open eyes")
    else:
        print(f"  ❌ FAIL: Expected < 0.3, got {avg_score:.2f}")
    print()
    
    # Reset detector
    detector.reset()
    
    # Test 2: Eyes Closed (Should be HIGH fatigue)
    print("TEST 2: Eyes Closed (Drowsy/Sleeping State)")
    print("-" * 70)
    img_closed = create_test_image_with_face(eyes_open=False)
    
    # Simulate prolonged eye closure
    scores = []
    for i in range(20):
        score, details = detector.detect(img_closed)
        scores.append(score)
        if i % 5 == 0:
            print(f"  Frame {i+1}: Fatigue = {score:.2f} ({score*100:.0f}%) - {details['status']}")
        time.sleep(0.05)
    
    final_score = scores[-1]
    print(f"\n  Final Score: {final_score:.2f} ({final_score*100:.0f}%)")
    
    if final_score > 0.6:
        print("  ✅ PASS: High fatigue detected for closed eyes")
    else:
        print(f"  ❌ FAIL: Expected > 0.6, got {final_score:.2f}")
    print()
    
    # Test 3: Blinking (Should spike then return to low)
    print("TEST 3: Blinking (Brief Eye Closure)")
    print("-" * 70)
    detector.reset()
    
    # Simulate blinking pattern
    print("  Simulating blink pattern...")
    scores = []
    
    # Eyes open
    for i in range(5):
        score, _ = detector.detect(img_open)
        scores.append(score)
    
    # Blink (eyes closed briefly)
    for i in range(3):
        score, _ = detector.detect(img_closed)
        scores.append(score)
    
    # Eyes open again
    for i in range(5):
        score, _ = detector.detect(img_open)
        scores.append(score)
    
    print(f"  Before blink: {scores[4]:.2f} ({scores[4]*100:.0f}%)")
    print(f"  During blink: {scores[7]:.2f} ({scores[7]*100:.0f}%)")
    print(f"  After blink:  {scores[-1]:.2f} ({scores[-1]*100:.0f}%)")
    
    if scores[4] < 0.3 and scores[-1] < 0.3:
        print("  ✅ PASS: Returns to low fatigue after blink")
    else:
        print(f"  ❌ FAIL: Should return to low fatigue")
    print()
    
    # Summary
    print("=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    print()
    print("Expected Behavior:")
    print("  • Eyes Open:   0-30% fatigue (LOW) ✅")
    print("  • Eyes Closed: 60-95% fatigue (HIGH) ✅")
    print("  • Blinking:    Brief spike, then returns to low ✅")
    print()
    print("The detector is working correctly if:")
    print("  1. Alert state shows LOW fatigue (0-30%)")
    print("  2. Drowsy/sleeping shows HIGH fatigue (60-95%)")
    print("  3. Blinking causes brief spike only")
    print()
    print("✅ Accuracy test complete!")
    print()

if __name__ == "__main__":
    try:
        test_fatigue_detector()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
