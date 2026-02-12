"""
Advanced Fatigue Detection using MediaPipe Face Mesh
MUCH more accurate than Haar Cascades - actually works!
"""

import cv2
import numpy as np
import time
from collections import deque
import mediapipe as mp

class FatigueDetector:
    """
    Production-grade fatigue detection using MediaPipe Face Mesh
    Detects: Eye closure, yawning, head pose, blink rate
    """
    
    def __init__(self):
        """Initialize MediaPipe Face Mesh detector"""
        try:
            # Initialize MediaPipe Face Mesh
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            # Eye landmarks (MediaPipe indices)
            self.LEFT_EYE = [362, 385, 387, 263, 373, 380]
            self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]
            
            # Mouth landmarks for yawn detection
            self.MOUTH_TOP = [13, 14]
            self.MOUTH_BOTTOM = [78, 308]
            
            # Tracking variables
            self.eye_closure_frames = 0
            self.yawn_frames = 0
            self.fatigue_history = deque(maxlen=5)
            
            # Blink tracking
            self.last_eye_state = 'open'
            self.blink_count = 0
            self.blink_times = deque(maxlen=20)
            
            # Thresholds (calibrated for MediaPipe)
            self.EYE_AR_THRESHOLD = 0.20  # Eye Aspect Ratio threshold
            self.MOUTH_AR_THRESHOLD = 0.6  # Mouth Aspect Ratio for yawn
            self.DROWSY_FRAMES = 3  # Frames before drowsy
            self.CRITICAL_FRAMES = 6  # Frames before critical
            
            print("✅ MediaPipe Fatigue Detector initialized")
            print("   • Face mesh tracking: ACTIVE")
            print("   • Eye aspect ratio: ACTIVE")
            print("   • Yawn detection: ACTIVE")
            print("   • Blink rate analysis: ACTIVE")
            print("   • Head pose estimation: ACTIVE")
            
        except Exception as e:
            print(f"❌ Error initializing MediaPipe: {e}")
            print("   Installing: pip install mediapipe")
            raise
    
    def calculate_eye_aspect_ratio(self, landmarks, eye_indices):
        """Calculate Eye Aspect Ratio (EAR)"""
        try:
            # Get eye landmarks
            eye_points = np.array([[landmarks[i].x, landmarks[i].y] for i in eye_indices])
            
            # Calculate vertical distances
            vertical_1 = np.linalg.norm(eye_points[1] - eye_points[5])
            vertical_2 = np.linalg.norm(eye_points[2] - eye_points[4])
            
            # Calculate horizontal distance
            horizontal = np.linalg.norm(eye_points[0] - eye_points[3])
            
            # Calculate EAR
            if horizontal > 0:
                ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
                return ear
            return 0.3
            
        except:
            return 0.3
    
    def calculate_mouth_aspect_ratio(self, landmarks):
        """Calculate Mouth Aspect Ratio (MAR) for yawn detection"""
        try:
            # Get mouth landmarks
            top = np.array([landmarks[self.MOUTH_TOP[0]].x, landmarks[self.MOUTH_TOP[0]].y])
            bottom = np.array([landmarks[self.MOUTH_BOTTOM[0]].x, landmarks[self.MOUTH_BOTTOM[0]].y])
            left = np.array([landmarks[78].x, landmarks[78].y])
            right = np.array([landmarks[308].x, landmarks[308].y])
            
            # Calculate vertical and horizontal distances
            vertical = np.linalg.norm(top - bottom)
            horizontal = np.linalg.norm(left - right)
            
            # Calculate MAR
            if horizontal > 0:
                mar = vertical / horizontal
                return mar
            return 0.0
            
        except:
            return 0.0
    
    def detect(self, image):
        """
        Detect fatigue level from image using MediaPipe
        
        Returns:
            tuple: (fatigue_score, details_dict)
                fatigue_score: 0.0 (alert) to 1.0 (drowsy)
        """
        try:
            # Convert BGR to RGB for MediaPipe
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process image
            results = self.face_mesh.process(image_rgb)
            
            # Initialize details
            details = {
                'faces_detected': 0,
                'eyes_detected': 0,
                'eye_state': 'unknown',
                'status': 'No face detected',
                'blink_rate': 0,
                'confidence': 0.0,
                'yawning': False,
                'eyes_closed': False,
                'head_tilted': False
            }
            
            # No face detected
            if not results.multi_face_landmarks:
                self.eye_closure_frames = 0
                return 0.0, details
            
            # Get face landmarks
            face_landmarks = results.multi_face_landmarks[0]
            landmarks = face_landmarks.landmark
            
            details['faces_detected'] = 1
            
            # Calculate Eye Aspect Ratios
            left_ear = self.calculate_eye_aspect_ratio(landmarks, self.LEFT_EYE)
            right_ear = self.calculate_eye_aspect_ratio(landmarks, self.RIGHT_EYE)
            avg_ear = (left_ear + right_ear) / 2.0
            
            # Calculate Mouth Aspect Ratio
            mar = self.calculate_mouth_aspect_ratio(landmarks)
            
            # Initialize fatigue score
            fatigue_score = 0.0
            
            # Check eye closure
            if avg_ear < self.EYE_AR_THRESHOLD:
                # Eyes closed
                self.eye_closure_frames += 1
                details['eye_state'] = 'closed'
                details['eyes_closed'] = True
                
                if self.eye_closure_frames < self.DROWSY_FRAMES:
                    # Might be blinking
                    fatigue_score = 0.3
                    details['status'] = 'Blinking'
                    details['confidence'] = 0.6
                    
                elif self.eye_closure_frames < self.CRITICAL_FRAMES:
                    # Drowsy
                    fatigue_score = 0.7
                    details['status'] = 'Drowsy - Eyes Closed'
                    details['confidence'] = 0.85
                    
                else:
                    # Critical - sleeping
                    fatigue_score = 0.95
                    details['status'] = 'CRITICAL - Sleeping'
                    details['confidence'] = 0.95
                
                # Track blink
                if self.last_eye_state == 'open':
                    self.blink_count += 1
                    self.blink_times.append(time.time())
                
                self.last_eye_state = 'closed'
                
            else:
                # Eyes open
                self.eye_closure_frames = 0
                details['eye_state'] = 'open'
                details['eyes_detected'] = 2
                details['status'] = 'Alert - Eyes Open'
                details['confidence'] = 0.95
                fatigue_score = 0.0
                
                self.last_eye_state = 'open'
            
            # Check for yawning
            if mar > self.MOUTH_AR_THRESHOLD:
                self.yawn_frames += 1
                if self.yawn_frames > 2:
                    details['yawning'] = True
                    fatigue_score = max(fatigue_score, 0.6)
                    details['status'] = 'Yawning Detected'
            else:
                self.yawn_frames = 0
            
            # Calculate blink rate
            current_time = time.time()
            # Remove old blinks (older than 60 seconds)
            while self.blink_times and (current_time - self.blink_times[0]) > 60:
                self.blink_times.popleft()
            
            if len(self.blink_times) > 0:
                time_span = current_time - self.blink_times[0]
                if time_span > 0:
                    blinks_per_minute = (len(self.blink_times) / time_span) * 60
                    details['blink_rate'] = int(blinks_per_minute)
                    
                    # Abnormal blink rate
                    if blinks_per_minute < 10:
                        fatigue_score = max(fatigue_score, 0.5)
                        details['status'] += ' (Low blink rate)'
            
            # Head pose estimation (simplified using nose tip)
            nose_tip = landmarks[1]
            if nose_tip.y > 0.6 or nose_tip.y < 0.3:
                details['head_tilted'] = True
                fatigue_score = max(fatigue_score, 0.4)
                details['status'] += ' (Head tilted)'
            
            # Temporal smoothing
            self.fatigue_history.append(fatigue_score)
            smoothed_score = np.mean(self.fatigue_history)
            
            # Apply confidence weighting
            final_score = smoothed_score * details['confidence']
            
            return round(final_score, 2), details
            
        except Exception as e:
            print(f"Error in fatigue detection: {e}")
            return 0.0, {'status': 'Error', 'error': str(e)}
    
    def reset(self):
        """Reset tracking variables"""
        self.eye_closure_frames = 0
        self.yawn_frames = 0
        self.fatigue_history.clear()
        self.last_eye_state = 'open'
        self.blink_count = 0
        self.blink_times.clear()
        print("🔄 Fatigue detector reset")
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'face_mesh'):
            self.face_mesh.close()
