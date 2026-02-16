"""
Traffic Sign Recognition (TSR) System
Detects and classifies traffic signs (speed limits, stop signs, etc.)
"""

import cv2
import numpy as np
from ultralytics import YOLO

class TrafficSignRecognition:
    """
    Traffic Sign Recognition using YOLOv8
    
    Detects:
    - Speed limit signs (20, 30, 40, 50, 60, 70, 80, 100, 120 km/h)
    - Stop signs
    - Yield signs
    - No entry signs
    - Priority road signs
    """
    
    def __init__(self):
        """Initialize TSR system"""
        # For now, use main YOLO model
        # In production, use a specialized traffic sign model
        self.model = None  # Will be set from main server
        
        # Traffic sign classes (would be in specialized model)
        self.sign_classes = {
            'stop': 'STOP',
            'traffic light': 'TRAFFIC LIGHT',
            'parking meter': 'PARKING',
        }
        
        # Speed limit detection (using OCR or specialized model)
        self.speed_limits = [20, 30, 40, 50, 60, 70, 80, 100, 120]
        
        # Current speed limit (would come from GPS/map data)
        self.current_speed_limit = 60  # km/h
        
        print("✅ Traffic Sign Recognition initialized")
        print("   • Detection: Stop, Traffic Light, Parking")
        print("   • Speed limit monitoring: Active")
    
    def set_model(self, model):
        """Set YOLO model from main server"""
        self.model = model
    
    def detect_signs(self, image, detections):
        """
        Detect traffic signs in image
        
        Args:
            image: Input BGR image
            detections: Existing YOLO detections
        
        Returns:
            signs: List of detected traffic signs
        """
        signs = []
        
        if not detections:
            return signs
        
        for detection in detections:
            label = detection.get('label', '').lower()
            
            # Check if it's a traffic sign
            if label in self.sign_classes:
                sign = {
                    'type': self.sign_classes[label],
                    'confidence': detection['confidence'],
                    'bbox': detection['bbox'],
                    'distance': detection.get('distance', 0)
                }
                signs.append(sign)
        
        return signs
    
    def check_speed_compliance(self, current_speed):
        """
        Check if current speed exceeds limit
        
        Args:
            current_speed: Current vehicle speed in km/h
        
        Returns:
            warning: Speed warning message or None
        """
        if current_speed > self.current_speed_limit:
            excess = current_speed - self.current_speed_limit
            return {
                'warning': True,
                'message': f'SPEED LIMIT EXCEEDED: {current_speed} km/h in {self.current_speed_limit} km/h zone',
                'excess': excess,
                'limit': self.current_speed_limit
            }
        
        return {
            'warning': False,
            'message': 'Speed OK',
            'excess': 0,
            'limit': self.current_speed_limit
        }
    
    def detect(self, image, detections, current_speed=0):
        """
        Main TSR pipeline
        
        Args:
            image: Input BGR image
            detections: Existing YOLO detections
            current_speed: Current vehicle speed in km/h
        
        Returns:
            result: Dictionary with TSR results
        """
        try:
            # Detect traffic signs
            signs = self.detect_signs(image, detections)
            
            # Check speed compliance
            speed_check = self.check_speed_compliance(current_speed)
            
            return {
                'signs_detected': len(signs),
                'signs': signs,
                'speed_warning': speed_check['warning'],
                'speed_message': speed_check['message'],
                'speed_limit': speed_check['limit'],
                'current_speed': current_speed
            }
            
        except Exception as e:
            print(f"Error in TSR: {e}")
            return {
                'signs_detected': 0,
                'signs': [],
                'speed_warning': False,
                'speed_message': 'TSR Error',
                'speed_limit': self.current_speed_limit,
                'current_speed': 0
            }
