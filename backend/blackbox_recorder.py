"""
Blackbox Recording System
Circular buffer recording with automatic event-triggered saving
"""

import cv2
import numpy as np
import os
import time
from collections import deque
from datetime import datetime
import json
import threading

class BlackboxRecorder:
    """
    Automotive-grade blackbox recorder with:
    - Circular buffer (last 30 seconds)
    - Event-triggered saving
    - Metadata logging
    - Forensic data preservation
    """
    
    def __init__(self, buffer_seconds=30, fps=2, output_dir='violations'):
        """
        Initialize blackbox recorder
        
        Args:
            buffer_seconds: Seconds of video to keep in buffer
            fps: Frames per second
            output_dir: Directory to save violation videos
        """
        self.buffer_seconds = buffer_seconds
        self.fps = fps
        self.max_frames = buffer_seconds * fps
        
        # Circular buffer for frames
        self.frame_buffer = deque(maxlen=self.max_frames)
        self.metadata_buffer = deque(maxlen=self.max_frames)
        
        # Output directory
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Recording state
        self.is_recording = False
        self.last_save_time = 0
        self.save_cooldown = 10  # seconds between saves
        
        # Statistics
        self.total_events_saved = 0
        self.total_frames_recorded = 0
        
        # Thread lock
        self.lock = threading.Lock()
        
        print("✅ Blackbox Recorder initialized")
        print(f"   • Buffer: {buffer_seconds} seconds ({self.max_frames} frames)")
        print(f"   • FPS: {fps}")
        print(f"   • Output: {output_dir}/")
        print(f"   • Forensic logging: ACTIVE")
    
    def add_frame(self, frame, metadata):
        """
        Add frame to circular buffer
        
        Args:
            frame: BGR image frame
            metadata: Dictionary with frame metadata
        """
        with self.lock:
            # Add timestamp
            metadata['timestamp'] = time.time()
            metadata['frame_number'] = self.total_frames_recorded
            
            # Add to buffer
            self.frame_buffer.append(frame.copy())
            self.metadata_buffer.append(metadata.copy())
            
            self.total_frames_recorded += 1
    
    def should_trigger_save(self, metadata):
        """
        Determine if event should trigger save
        
        Triggers:
        - Critical collision warning (distance < 2m)
        - Critical fatigue (> 70%)
        - Lane departure warning
        - Pedestrian crossing intent
        - Speed limit violation
        
        Args:
            metadata: Frame metadata
        
        Returns:
            should_save: Boolean
            event_type: Type of event
        """
        # Check cooldown
        if time.time() - self.last_save_time < self.save_cooldown:
            return False, None
        
        # Critical collision
        if metadata.get('closest_distance', 100) < 2.0:
            return True, 'CRITICAL_COLLISION'
        
        # Critical fatigue
        if metadata.get('fatigue_level', 0) > 0.7:
            return True, 'CRITICAL_FATIGUE'
        
        # Lane departure
        if metadata.get('lane_departure', False):
            return True, 'LANE_DEPARTURE'
        
        # Pedestrian crossing
        if metadata.get('pedestrian_crossing', False):
            return True, 'PEDESTRIAN_CROSSING'
        
        # Speed violation
        if metadata.get('speed_violation', False):
            return True, 'SPEED_VIOLATION'
        
        return False, None
    
    def save_event(self, event_type, trigger_metadata):
        """
        Save buffered frames to video file
        
        Args:
            event_type: Type of event (e.g., 'CRITICAL_COLLISION')
            trigger_metadata: Metadata of triggering frame
        """
        with self.lock:
            if len(self.frame_buffer) == 0:
                return None
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{event_type}_{timestamp}.mp4"
            filepath = os.path.join(self.output_dir, filename)
            
            # Get frame dimensions
            height, width = self.frame_buffer[0].shape[:2]
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(filepath, fourcc, self.fps, (width, height))
            
            if not out.isOpened():
                print(f"❌ Failed to create video writer: {filepath}")
                return None
            
            # Write frames
            frames_written = 0
            for frame in self.frame_buffer:
                out.write(frame)
                frames_written += 1
            
            out.release()
            
            # Save metadata - convert numpy types to native Python types
            metadata_file = filepath.replace('.mp4', '_metadata.json')
            metadata_summary = {
                'event_type': event_type,
                'timestamp': timestamp,
                'frames_count': int(frames_written),
                'duration_seconds': float(frames_written / self.fps),
                'trigger_frame': self._convert_to_serializable(trigger_metadata),
                'buffer_metadata': [self._convert_to_serializable(m) for m in list(self.metadata_buffer)]
            }
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata_summary, f, indent=2)
            
            # Update statistics
            self.total_events_saved += 1
            self.last_save_time = time.time()
            
            print(f"📹 Blackbox saved: {filename}")
            print(f"   • Event: {event_type}")
            print(f"   • Frames: {frames_written}")
            print(f"   • Duration: {frames_written / self.fps:.1f}s")
            
            return filepath
    
    def _convert_to_serializable(self, obj):
        """
        Convert numpy types and other non-serializable types to native Python types
        """
        if isinstance(obj, dict):
            return {key: self._convert_to_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_serializable(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(self._convert_to_serializable(item) for item in obj)
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif isinstance(obj, (np.integer, int)):
            return int(obj)
        elif isinstance(obj, (np.floating, float)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif obj is None:
            return None
        elif isinstance(obj, str):
            return obj
        else:
            # Try to convert to string as last resort
            try:
                return str(obj)
            except:
                return None
    
    def process_frame(self, frame, metadata):
        """
        Process frame and check for trigger events
        
        Args:
            frame: BGR image frame
            metadata: Frame metadata
        
        Returns:
            saved_file: Path to saved file if triggered, None otherwise
        """
        # Add frame to buffer
        self.add_frame(frame, metadata)
        
        # Check for trigger
        should_save, event_type = self.should_trigger_save(metadata)
        
        if should_save:
            return self.save_event(event_type, metadata)
        
        return None
    
    def get_statistics(self):
        """
        Get recorder statistics
        
        Returns:
            stats: Dictionary with statistics
        """
        return {
            'total_events_saved': self.total_events_saved,
            'total_frames_recorded': self.total_frames_recorded,
            'buffer_size': len(self.frame_buffer),
            'buffer_capacity': self.max_frames,
            'buffer_duration': len(self.frame_buffer) / self.fps,
            'output_directory': self.output_dir
        }
    
    def clear_buffer(self):
        """Clear the circular buffer"""
        with self.lock:
            self.frame_buffer.clear()
            self.metadata_buffer.clear()
            print("🔄 Blackbox buffer cleared")
