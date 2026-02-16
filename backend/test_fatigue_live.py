"""
Live Fatigue Detection Test
Tests the fatigue detector with your webcam in real-time
"""

import cv2
import numpy as np
from fatigue_detector_advanced import FatigueDetector
import time

def main():
    print("=" * 70)
    print("  LIVE FATIGUE DETECTION TEST")
    print("=" * 70)
    print("\nInitializing fatigue detector...")
    
    # Initialize detector
    detector = FatigueDetector()
    
    print("\nOpening webcam...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ ERROR: Could not open webcam!")
        return
    
    print("✅ Webcam opened successfully!")
    print("\nINSTRUCTIONS:")
    print("  • Look at the camera normally")
    print("  • Close your eyes to test drowsiness detection")
    print("  • Open your eyes to test alert state")
    print("  • Press 'q' to quit")
    print("\n" + "=" * 70)
    
    frame_count = 0
    start_time = time.time()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read frame")
            break
        
        frame_count += 1
        
        # Run detection
        fatigue_score, details = detector.detect(frame)
        
        # Display info on frame
        h, w = frame.shape[:2]
        
        # Background for text
        cv2.rectangle(frame, (10, 10), (w-10, 180), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (w-10, 180), (0, 255, 0), 2)
        
        # Fatigue score
        color = (0, 255, 0) if fatigue_score < 0.3 else (0, 165, 255) if fatigue_score < 0.6 else (0, 0, 255)
        cv2.putText(frame, f"FATIGUE: {fatigue_score:.2f} ({int(fatigue_score*100)}%)", 
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # Status
        status = details.get('status', 'Unknown')
        cv2.putText(frame, f"STATUS: {status}", 
                    (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Detection details
        faces = details.get('faces_detected', 0)
        eyes = details.get('eyes_detected', 0)
        eye_state = details.get('eye_state', 'unknown')
        
        cv2.putText(frame, f"Faces: {faces} | Eyes: {eyes} | State: {eye_state}", 
                    (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Method
        method = details.get('method', 'MediaPipe' if detector.mediapipe_available else 'OpenCV')
        cv2.putText(frame, f"Method: {method}", 
                    (20, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # FPS
        elapsed = time.time() - start_time
        fps = frame_count / elapsed if elapsed > 0 else 0
        cv2.putText(frame, f"FPS: {fps:.1f}", 
                    (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Console output every 30 frames
        if frame_count % 30 == 0:
            print(f"\n[Frame {frame_count}]")
            print(f"  Fatigue: {fatigue_score:.2f} ({int(fatigue_score*100)}%)")
            print(f"  Status: {status}")
            print(f"  Faces: {faces}, Eyes: {eyes}, State: {eye_state}")
            print(f"  Method: {method}")
        
        # Show frame
        cv2.imshow('Fatigue Detection Test', frame)
        
        # Check for quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n" + "=" * 70)
    print("  TEST COMPLETED")
    print("=" * 70)
    print(f"Total frames processed: {frame_count}")
    print(f"Average FPS: {fps:.1f}")
    print("\nIf fatigue was always 0:")
    print("  1. Check if your face was visible to the camera")
    print("  2. Ensure good lighting conditions")
    print("  3. Try moving closer to the camera")
    print("  4. Check backend/server.py logs for errors")

if __name__ == "__main__":
    main()
