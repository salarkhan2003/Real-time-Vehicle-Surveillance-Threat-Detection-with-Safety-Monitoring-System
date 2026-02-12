"""
Reliable Fatigue Detection using OpenCV DNN Face Detector
Works without MediaPipe - uses pre-trained deep learning models
"""

import cv2
import numpy as np
import time
from collections import deque
import os

class FatigueDetector:
    """
    Production-grade fatigue detection using OpenCV DNN
    More accurate than Haar Cascades, no MediaPipe required
    """
    
    def __init__(self):
        """Initialize DNN face detector"""
        try:
            # Load DNN face detector (more accurate than Haar Cascades)
            model_file = "res10_300x300_ssd_iter_140000.caffemodel"
            config_file = "deploy.prototxt"
            
            # Try to load from current directory
            if not os.path.exists(model_file):
                print("⚠️  DNN model not found, downloading...")
                self._download_models()
            
            self.face_net = cv2.dnn.readNetFromCaffe(config_file, model_file)
            
            # Load eye cascade (still useful for eye detection)
            self.eye_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_eye.xml'
            )
            
            # Tracking variables
            self.eye_closure_frames = 0
            self.alert_frames = 0
            self.fatigue_history = deque(maxlen=5)
            
            # Blink tracking
            self.last_eye_state = 'open'
            self.blink_count = 0
            self.blink_times = deque(maxlen=20)
            
            # Thresholds
            self.DROWSY_FRAMES = 3
            self.CRITICAL_FRAMES = 6
            
            print("✅ DNN Fatigue Detector initialized")
            print("   • Deep learning face detection: ACTIVE")
            print("   • Eye closure tracking: ACTIVE")
            print("   • Blink rate analysis: ACTIVE")
            print("   • Fast response: ENABLED")
            
        except Exception as e:
            print(f"❌ Error initializing DNN detector: {e}")
            print("   Falling back to basic detection...")
            self.face_net = None
            self.eye_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_eye.xml'
            )
    
    def _download_models(self):
        """Download DNN models if not present"""
        import urllib.request
        
        print("Downloading face detection models...")
        
        # Download prototxt
        prototxt_url = "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt"
        urllib.request.urlretrieve(prototxt_url, "deploy.prototxt")
        
        # Download caffemodel
        model_url = "https://github.com/opencv/opencv_3rdparty/raw/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel"
        urllib.request.urlretrieve(model_url, "res10_300x300_ssd_iter_140000.caffemodel")
        
        print("✅ Models downloaded successfully")
    
    def detect_face_dnn(self, image):
        """Detect face using DNN (more accurate)"""
        try:
            h, w = image.shape[:2]
            blob = cv2.dnn.blobFromImage(
                cv2.resize(image, (300, 300)), 
                1.0, 
                (300, 300), 
                (104.0, 177.0, 123.0)
            )
            
            self.face_net.setInput(blob)
            detections = self.face_net.forward()
            
            faces = []
            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                
                if confidence > 0.5:
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (x, y, x2, y2) = box.astype("int")
                    
                    # Ensure coordinates are within image bounds
                    x = max(0, x)
                    y = max(0, y)
                    x2 = min(w, x2)
                    y2 = min(h, y2)
                    
                    faces.append((x, y, x2-x, y2-y))
            
            return faces
            
        except:
            return []
    
    def detect(self, image):
        """
        Detect fatigue level from image
        
        Returns:
            tuple: (fatigue_score, details_dict)
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Enhance contrast
            gray = cv2.equalizeHist(gray)
            
            # Initialize details
            details = {
                'faces_detected': 0,
                'eyes_detected': 0,
                'eye_state': 'unknown',
                'status': 'No face detected',
                'blink_rate': 0,
                'confidence': 0.0,
                'eyes_closed': False
            }
            
            # Detect face using DNN
            if self.face_net is not None:
                faces = self.detect_face_dnn(image)
            else:
                # Fallback to Haar Cascade
                face_cascade = cv2.CascadeClassifier(
                    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                )
                faces = face_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
                )
            
            # No face detected
            if len(faces) == 0:
                self.eye_closure_frames = 0
                self.alert_frames += 1
                return 0.0, details
            
            details['faces_detected'] = len(faces)
            
            # Process largest face
            faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
            x, y, w, h = faces[0]
            
            # Extract face region
            face_roi = gray[y:y+h, x:x+w]
            
            # Focus on upper half (where eyes are)
            eye_region_height = int(h * 0.6)
            eye_region = face_roi[0:eye_region_height, :]
            
            # Detect eyes
            eyes = self.eye_cascade.detectMultiScale(
                eye_region,
                scaleFactor=1.05,
                minNeighbors=3,
                minSize=(int(w * 0.15), int(h * 0.1)),
                maxSize=(int(w * 0.4), int(h * 0.3))
            )
            
            num_eyes = len(eyes)
            details['eyes_detected'] = num_eyes
            
            # Calculate fatigue score
            fatigue_score = 0.0
            
            if num_eyes >= 2:
                # Both eyes detected - ALERT
                details['eye_state'] = 'open'
                details['status'] = 'Alert - Eyes Open'
                details['confidence'] = 0.95
                
                self.eye_closure_frames = 0
                self.alert_frames += 1
                
                # Track blink
                if self.last_eye_state == 'closed':
                    self.blink_count += 1
                    self.blink_times.append(time.time())
                
                self.last_eye_state = 'open'
                fatigue_score = 0.0
                
            elif num_eyes == 1:
                # One eye detected - PARTIAL
                details['eye_state'] = 'partial'
                details['status'] = 'Partial Eye Closure'
                details['confidence'] = 0.7
                
                self.eye_closure_frames += 1
                self.alert_frames = 0
                
                if self.eye_closure_frames < 5:
                    fatigue_score = 0.3
                else:
                    fatigue_score = 0.5
                
            else:
                # No eyes detected - CLOSED
                details['eye_state'] = 'closed'
                details['eyes_closed'] = True
                
                self.eye_closure_frames += 1
                self.alert_frames = 0
                self.last_eye_state = 'closed'
                
                if self.eye_closure_frames < self.DROWSY_FRAMES:
                    # Might be blinking
                    fatigue_score = 0.4
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
            
            # Calculate blink rate
            current_time = time.time()
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
        self.alert_frames = 0
        self.fatigue_history.clear()
        self.last_eye_state = 'open'
        self.blink_count = 0
        self.blink_times.clear()
        print("🔄 Fatigue detector reset")
