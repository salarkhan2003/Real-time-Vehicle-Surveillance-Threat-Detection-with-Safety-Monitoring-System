"""
Lane Keep Assist (LKA) System
Implements lane detection, departure warning, and steering angle calculation
"""

import cv2
import numpy as np
from collections import deque

class LaneKeepAssist:
    """
    Advanced Lane Keep Assist with:
    - Perspective transformation (bird's eye view)
    - Color filtering (HLS space)
    - Sliding window search
    - Polynomial fitting
    - Lane departure warning
    - Steering angle calculation
    """
    
    def __init__(self, image_width=1280, image_height=720):
        """Initialize LKA system"""
        self.image_width = image_width
        self.image_height = image_height
        
        # Perspective transform points (trapezoid to rectangle)
        # These define the region of interest for lane detection
        self.src_points = np.float32([
            [int(image_width * 0.45), int(image_height * 0.65)],  # Top-left
            [int(image_width * 0.55), int(image_height * 0.65)],  # Top-right
            [int(image_width * 0.1), image_height],               # Bottom-left
            [int(image_width * 0.9), image_height]                # Bottom-right
        ])
        
        self.dst_points = np.float32([
            [int(image_width * 0.25), 0],                         # Top-left
            [int(image_width * 0.75), 0],                         # Top-right
            [int(image_width * 0.25), image_height],              # Bottom-left
            [int(image_width * 0.75), image_height]               # Bottom-right
        ])
        
        # Compute perspective transform matrices
        self.M = cv2.getPerspectiveTransform(self.src_points, self.dst_points)
        self.M_inv = cv2.getPerspectiveTransform(self.dst_points, self.src_points)
        
        # Sliding window parameters
        self.n_windows = 9
        self.margin = 100
        self.minpix = 50
        
        # Lane history for smoothing
        self.left_fit_history = deque(maxlen=5)
        self.right_fit_history = deque(maxlen=5)
        
        # Lane departure thresholds
        self.LANE_WIDTH_METERS = 3.7  # Standard lane width in meters
        self.DEPARTURE_THRESHOLD = 0.3  # 30cm from lane edge
        
        # Focal length for steering angle calculation (calibrated)
        self.FOCAL_LENGTH = 600  # pixels
        
        # Meters per pixel in y dimension
        self.ym_per_pix = 30 / 720  # 30 meters per 720 pixels
        # Meters per pixel in x dimension
        self.xm_per_pix = 3.7 / 700  # 3.7 meters per 700 pixels
        
        print("✅ Lane Keep Assist initialized")
        print(f"   • Image size: {image_width}x{image_height}")
        print(f"   • Lane width: {self.LANE_WIDTH_METERS}m")
        print(f"   • Departure threshold: {self.DEPARTURE_THRESHOLD}m")
    
    def preprocess_image(self, image):
        """
        Preprocess image for lane detection
        
        Steps:
        1. Convert to HLS color space
        2. Apply color thresholds for white and yellow lines
        3. Apply Sobel edge detection
        4. Combine color and gradient thresholds
        
        Args:
            image: Input BGR image
        
        Returns:
            binary: Binary image with lane lines highlighted
        """
        # Convert to HLS color space
        hls = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
        h_channel = hls[:, :, 0]
        l_channel = hls[:, :, 1]
        s_channel = hls[:, :, 2]
        
        # White line detection (high lightness)
        white_binary = np.zeros_like(l_channel)
        white_binary[(l_channel > 200)] = 1
        
        # Yellow line detection (hue + saturation)
        yellow_binary = np.zeros_like(s_channel)
        yellow_binary[((h_channel >= 15) & (h_channel <= 35)) & 
                     ((s_channel >= 40) & (s_channel <= 255))] = 1
        
        # Combine color thresholds
        color_binary = np.zeros_like(s_channel)
        color_binary[(white_binary == 1) | (yellow_binary == 1)] = 1
        
        # Sobel edge detection (gradient in x direction)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        abs_sobelx = np.absolute(sobelx)
        scaled_sobel = np.uint8(255 * abs_sobelx / np.max(abs_sobelx))
        
        # Gradient threshold
        gradient_binary = np.zeros_like(scaled_sobel)
        gradient_binary[(scaled_sobel >= 20) & (scaled_sobel <= 100)] = 1
        
        # Combine color and gradient
        combined_binary = np.zeros_like(gradient_binary)
        combined_binary[(color_binary == 1) | (gradient_binary == 1)] = 1
        
        return combined_binary
    
    def perspective_transform(self, image):
        """
        Apply perspective transform to get bird's eye view
        
        Args:
            image: Binary image
        
        Returns:
            warped: Bird's eye view image
        """
        img_size = (image.shape[1], image.shape[0])
        warped = cv2.warpPerspective(image, self.M, img_size, flags=cv2.INTER_LINEAR)
        return warped
    
    def find_lane_pixels(self, binary_warped):
        """
        Find lane line pixels using sliding window search
        
        Algorithm:
        1. Take histogram of bottom half of image
        2. Find peaks (left and right lane bases)
        3. Use sliding windows to follow lines up
        4. Collect pixel indices
        
        Args:
            binary_warped: Binary bird's eye view image
        
        Returns:
            leftx, lefty, rightx, righty: Pixel coordinates of lane lines
        """
        # Take histogram of bottom half
        histogram = np.sum(binary_warped[binary_warped.shape[0]//2:, :], axis=0)
        
        # Find peaks (lane bases)
        midpoint = len(histogram) // 2
        leftx_base = np.argmax(histogram[:midpoint])
        rightx_base = np.argmax(histogram[midpoint:]) + midpoint
        
        # Window height
        window_height = binary_warped.shape[0] // self.n_windows
        
        # Identify x and y positions of all nonzero pixels
        nonzero = binary_warped.nonzero()
        nonzeroy = np.array(nonzero[0])
        nonzerox = np.array(nonzero[1])
        
        # Current positions
        leftx_current = leftx_base
        rightx_current = rightx_base
        
        # Lists to receive lane pixel indices
        left_lane_inds = []
        right_lane_inds = []
        
        # Step through windows
        for window in range(self.n_windows):
            # Window boundaries
            win_y_low = binary_warped.shape[0] - (window + 1) * window_height
            win_y_high = binary_warped.shape[0] - window * window_height
            
            # Left window boundaries
            win_xleft_low = leftx_current - self.margin
            win_xleft_high = leftx_current + self.margin
            
            # Right window boundaries
            win_xright_low = rightx_current - self.margin
            win_xright_high = rightx_current + self.margin
            
            # Identify nonzero pixels in window
            good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & 
                             (nonzerox >= win_xleft_low) & (nonzerox < win_xleft_high)).nonzero()[0]
            good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & 
                              (nonzerox >= win_xright_low) & (nonzerox < win_xright_high)).nonzero()[0]
            
            # Append indices
            left_lane_inds.append(good_left_inds)
            right_lane_inds.append(good_right_inds)
            
            # Recenter window if enough pixels found
            if len(good_left_inds) > self.minpix:
                leftx_current = int(np.mean(nonzerox[good_left_inds]))
            if len(good_right_inds) > self.minpix:
                rightx_current = int(np.mean(nonzerox[good_right_inds]))
        
        # Concatenate indices
        left_lane_inds = np.concatenate(left_lane_inds)
        right_lane_inds = np.concatenate(right_lane_inds)
        
        # Extract pixel positions
        leftx = nonzerox[left_lane_inds]
        lefty = nonzeroy[left_lane_inds]
        rightx = nonzerox[right_lane_inds]
        righty = nonzeroy[right_lane_inds]
        
        return leftx, lefty, rightx, righty
    
    def fit_polynomial(self, leftx, lefty, rightx, righty):
        """
        Fit second-order polynomial to lane lines
        
        Formula: x = Ay² + By + C
        
        Args:
            leftx, lefty, rightx, righty: Lane pixel coordinates
        
        Returns:
            left_fit, right_fit: Polynomial coefficients [A, B, C]
        """
        if len(leftx) == 0 or len(lefty) == 0:
            return None, None
        
        # Fit polynomial
        left_fit = np.polyfit(lefty, leftx, 2)
        right_fit = np.polyfit(righty, rightx, 2)
        
        # Add to history for smoothing
        self.left_fit_history.append(left_fit)
        self.right_fit_history.append(right_fit)
        
        # Average over history
        left_fit_smooth = np.mean(self.left_fit_history, axis=0)
        right_fit_smooth = np.mean(self.right_fit_history, axis=0)
        
        return left_fit_smooth, right_fit_smooth
    
    def calculate_curvature(self, left_fit, right_fit, y_eval):
        """
        Calculate radius of curvature in meters
        
        Formula: R = [(1 + (2Ay + B)²)^(3/2)] / |2A|
        
        Args:
            left_fit, right_fit: Polynomial coefficients
            y_eval: Y position to evaluate (usually bottom of image)
        
        Returns:
            left_curverad, right_curverad: Radius of curvature in meters
        """
        # Convert from pixels to meters
        left_fit_cr = np.polyfit(
            np.linspace(0, self.image_height, self.image_height) * self.ym_per_pix,
            left_fit[0] * (np.linspace(0, self.image_height, self.image_height) ** 2) + 
            left_fit[1] * np.linspace(0, self.image_height, self.image_height) + 
            left_fit[2],
            2
        )
        
        right_fit_cr = np.polyfit(
            np.linspace(0, self.image_height, self.image_height) * self.ym_per_pix,
            right_fit[0] * (np.linspace(0, self.image_height, self.image_height) ** 2) + 
            right_fit[1] * np.linspace(0, self.image_height, self.image_height) + 
            right_fit[2],
            2
        )
        
        # Calculate curvature
        y_eval_m = y_eval * self.ym_per_pix
        left_curverad = ((1 + (2 * left_fit_cr[0] * y_eval_m + left_fit_cr[1]) ** 2) ** 1.5) / np.abs(2 * left_fit_cr[0])
        right_curverad = ((1 + (2 * right_fit_cr[0] * y_eval_m + right_fit_cr[1]) ** 2) ** 1.5) / np.abs(2 * right_fit_cr[0])
        
        return left_curverad, right_curverad
    
    def calculate_lane_offset(self, left_fit, right_fit):
        """
        Calculate vehicle offset from lane center
        
        Formula: offset = (lane_center - car_center) * xm_per_pix
        
        Args:
            left_fit, right_fit: Polynomial coefficients
        
        Returns:
            offset: Distance from lane center in meters (positive = right, negative = left)
        """
        # Calculate lane positions at bottom of image
        y_eval = self.image_height
        left_lane_pos = left_fit[0] * y_eval ** 2 + left_fit[1] * y_eval + left_fit[2]
        right_lane_pos = right_fit[0] * y_eval ** 2 + right_fit[1] * y_eval + right_fit[2]
        
        # Lane center
        lane_center = (left_lane_pos + right_lane_pos) / 2
        
        # Car center (assume camera is centered)
        car_center = self.image_width / 2
        
        # Offset in meters
        offset = (lane_center - car_center) * self.xm_per_pix
        
        return offset
    
    def calculate_steering_angle(self, offset):
        """
        Calculate required steering angle
        
        Formula: θ = arctan(offset / focal_length)
        
        Args:
            offset: Lane offset in meters
        
        Returns:
            angle: Steering angle in degrees
        """
        # Convert offset to pixels
        offset_pixels = offset / self.xm_per_pix
        
        # Calculate angle
        angle_rad = np.arctan(offset_pixels / self.FOCAL_LENGTH)
        angle_deg = np.degrees(angle_rad)
        
        return angle_deg
    
    def detect(self, image):
        """
        Main detection pipeline
        
        Args:
            image: Input BGR image
        
        Returns:
            result: Dictionary with lane detection results
        """
        try:
            # Resize image if needed
            if image.shape[1] != self.image_width or image.shape[0] != self.image_height:
                image = cv2.resize(image, (self.image_width, self.image_height))
            
            # Preprocess
            binary = self.preprocess_image(image)
            
            # Perspective transform
            binary_warped = self.perspective_transform(binary)
            
            # Find lane pixels
            leftx, lefty, rightx, righty = self.find_lane_pixels(binary_warped)
            
            # Check if enough pixels found
            if len(leftx) < 100 or len(rightx) < 100:
                return {
                    'detected': False,
                    'offset': 0.0,
                    'steering_angle': 0.0,
                    'curvature': 0.0,
                    'departure_warning': False,
                    'status': 'No lanes detected'
                }
            
            # Fit polynomial
            left_fit, right_fit = self.fit_polynomial(leftx, lefty, rightx, righty)
            
            if left_fit is None or right_fit is None:
                return {
                    'detected': False,
                    'offset': 0.0,
                    'steering_angle': 0.0,
                    'curvature': 0.0,
                    'departure_warning': False,
                    'status': 'No lanes detected'
                }
            
            # Calculate metrics
            offset = self.calculate_lane_offset(left_fit, right_fit)
            steering_angle = self.calculate_steering_angle(offset)
            left_curv, right_curv = self.calculate_curvature(left_fit, right_fit, self.image_height)
            avg_curvature = (left_curv + right_curv) / 2
            
            # Lane departure warning
            departure_warning = abs(offset) > self.DEPARTURE_THRESHOLD
            
            # Determine status
            if departure_warning:
                if offset > 0:
                    status = 'DRIFTING RIGHT'
                else:
                    status = 'DRIFTING LEFT'
            else:
                status = 'CENTERED'
            
            return {
                'detected': True,
                'offset': float(offset),
                'steering_angle': float(steering_angle),
                'curvature': float(avg_curvature),
                'departure_warning': bool(departure_warning),
                'status': status,
                'left_fit': left_fit.tolist(),
                'right_fit': right_fit.tolist(),
                'visualization': {
                    'lane_detected': True
                }
            }
            
        except Exception as e:
            print(f"⚠️  LKA Error: {e}")
            return {
                'detected': False,
                'offset': 0.0,
                'steering_angle': 0.0,
                'curvature': 0.0,
                'departure_warning': False,
                'status': 'No lanes detected'
            }
