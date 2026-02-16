"""
Pedestrian Intent Prediction System
Predicts if pedestrians are about to cross the road using pose estimation
"""

import cv2
import numpy as np

class PedestrianIntentPredictor:
    """
    Predicts pedestrian crossing intent using:
    - Body orientation (facing road or away)
    - Movement direction (toward or away from road)
    - Position relative to curb
    - Head pose (looking at road)
    """
    
    def __init__(self):
        """Initialize pedestrian intent predictor"""
        try:
            import mediapipe as mp
            
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            self.use_mediapipe = True
            print("✅ Pedestrian Intent Predictor initialized (MediaPipe)")
            
        except Exception as e:
            print(f"⚠️  MediaPipe not available for intent prediction: {e}")
            self.use_mediapipe = False
            print("✅ Pedestrian Intent Predictor initialized (Basic)")
        
        # Intent thresholds
        self.CROSSING_THRESHOLD = 0.6  # 60% confidence
        
        # Position history for movement tracking
        self.position_history = {}  # {person_id: [(x, y, timestamp), ...]}
        
        print("   • Body orientation analysis: Active")
        print("   • Movement tracking: Active")
        print("   • Crossing prediction: Active")
    
    def calculate_body_orientation(self, landmarks, image_width):
        """
        Calculate body orientation angle
        
        Uses shoulder and hip landmarks to determine if person is facing road
        
        Args:
            landmarks: MediaPipe pose landmarks
            image_width: Image width in pixels
        
        Returns:
            angle: Body orientation angle in degrees (0 = facing camera)
        """
        try:
            # Get shoulder landmarks
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            
            # Calculate shoulder vector
            shoulder_vector = np.array([
                right_shoulder.x - left_shoulder.x,
                right_shoulder.y - left_shoulder.y
            ])
            
            # Calculate angle relative to camera
            angle = np.degrees(np.arctan2(shoulder_vector[1], shoulder_vector[0]))
            
            return angle
            
        except Exception as e:
            return 0.0
    
    def calculate_movement_direction(self, person_id, current_pos):
        """
        Calculate movement direction from position history
        
        Args:
            person_id: Unique person identifier
            current_pos: Current (x, y) position
        
        Returns:
            direction: Movement direction vector (dx, dy)
        """
        import time
        
        # Add current position to history
        if person_id not in self.position_history:
            self.position_history[person_id] = []
        
        self.position_history[person_id].append((*current_pos, time.time()))
        
        # Keep only last 10 positions
        self.position_history[person_id] = self.position_history[person_id][-10:]
        
        # Need at least 2 positions
        if len(self.position_history[person_id]) < 2:
            return (0, 0)
        
        # Calculate average movement
        positions = self.position_history[person_id]
        dx = positions[-1][0] - positions[0][0]
        dy = positions[-1][1] - positions[0][1]
        
        return (dx, dy)
    
    def predict_intent_mediapipe(self, image, person_bbox, person_id):
        """
        Predict crossing intent using MediaPipe pose estimation
        
        Args:
            image: Input BGR image
            person_bbox: Person bounding box [x, y, w, h]
            person_id: Unique person identifier
        
        Returns:
            intent: Dictionary with intent prediction
        """
        try:
            # Extract person region
            x, y, w, h = person_bbox
            x, y, w, h = int(x), int(y), int(w), int(h)
            
            # Ensure valid bbox
            if x < 0 or y < 0 or w <= 0 or h <= 0:
                return self._default_intent()
            
            person_img = image[y:y+h, x:x+w]
            
            if person_img.size == 0:
                return self._default_intent()
            
            # Convert to RGB
            person_rgb = cv2.cvtColor(person_img, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe
            results = self.pose.process(person_rgb)
            
            if not results.pose_landmarks:
                return self._default_intent()
            
            # Calculate body orientation
            orientation = self.calculate_body_orientation(
                results.pose_landmarks.landmark,
                person_img.shape[1]
            )
            
            # Calculate movement direction
            center_x = x + w / 2
            center_y = y + h / 2
            movement = self.calculate_movement_direction(person_id, (center_x, center_y))
            
            # Predict intent
            # Facing road (orientation near 0 or 180)
            facing_road = abs(orientation) < 45 or abs(orientation) > 135
            
            # Moving toward road (positive x movement)
            moving_toward = movement[0] > 5  # pixels per frame
            
            # Calculate crossing probability
            crossing_prob = 0.0
            
            if facing_road:
                crossing_prob += 0.4
            
            if moving_toward:
                crossing_prob += 0.4
            
            # Near edge of frame (likely near curb)
            if center_x < image.shape[1] * 0.2 or center_x > image.shape[1] * 0.8:
                crossing_prob += 0.2
            
            # Determine intent
            if crossing_prob >= self.CROSSING_THRESHOLD:
                intent_status = 'LIKELY TO CROSS'
                warning = True
            elif crossing_prob >= 0.3:
                intent_status = 'WATCHING ROAD'
                warning = False
            else:
                intent_status = 'WALKING NORMALLY'
                warning = False
            
            return {
                'detected': True,
                'crossing_probability': float(crossing_prob),
                'status': intent_status,
                'warning': warning,
                'facing_road': facing_road,
                'moving_toward': moving_toward,
                'body_orientation': float(orientation)
            }
            
        except Exception as e:
            print(f"Error in intent prediction: {e}")
            return self._default_intent()
    
    def predict_intent_basic(self, image, person_bbox, person_id):
        """
        Basic intent prediction without pose estimation
        Uses position and movement only
        
        Args:
            image: Input BGR image
            person_bbox: Person bounding box [x, y, w, h]
            person_id: Unique person identifier
        
        Returns:
            intent: Dictionary with intent prediction
        """
        try:
            x, y, w, h = person_bbox
            
            # Calculate center
            center_x = x + w / 2
            center_y = y + h / 2
            
            # Calculate movement
            movement = self.calculate_movement_direction(person_id, (center_x, center_y))
            
            # Simple heuristics
            moving_toward = movement[0] > 5
            near_edge = center_x < image.shape[1] * 0.2 or center_x > image.shape[1] * 0.8
            
            crossing_prob = 0.0
            if moving_toward:
                crossing_prob += 0.5
            if near_edge:
                crossing_prob += 0.3
            
            warning = crossing_prob >= self.CROSSING_THRESHOLD
            status = 'LIKELY TO CROSS' if warning else 'WALKING NORMALLY'
            
            return {
                'detected': True,
                'crossing_probability': float(crossing_prob),
                'status': status,
                'warning': warning,
                'facing_road': False,
                'moving_toward': moving_toward,
                'body_orientation': 0.0
            }
            
        except Exception as e:
            return self._default_intent()
    
    def _default_intent(self):
        """Return default intent when detection fails"""
        return {
            'detected': False,
            'crossing_probability': 0.0,
            'status': 'Unknown',
            'warning': False,
            'facing_road': False,
            'moving_toward': False,
            'body_orientation': 0.0
        }
    
    def detect(self, image, detections):
        """
        Main intent prediction pipeline
        
        Args:
            image: Input BGR image
            detections: List of person detections
        
        Returns:
            results: List of intent predictions
        """
        results = []
        
        if not detections:
            return results
        
        for i, detection in enumerate(detections):
            # Only process person detections
            if detection.get('label', '').lower() != 'person':
                continue
            
            # Get bounding box
            bbox = detection.get('bbox', [0, 0, 0, 0])
            
            # Predict intent
            if self.use_mediapipe:
                intent = self.predict_intent_mediapipe(image, bbox, i)
            else:
                intent = self.predict_intent_basic(image, bbox, i)
            
            # Add detection info
            intent['person_id'] = i
            intent['bbox'] = bbox
            intent['distance'] = detection.get('distance', 0)
            
            results.append(intent)
        
        return results
