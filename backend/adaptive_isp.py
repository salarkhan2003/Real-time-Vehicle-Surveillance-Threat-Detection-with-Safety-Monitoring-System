"""
Adaptive Image Signal Processing (ISP)
Auto-adjusts for night, rain, fog, and low-visibility conditions
"""

import cv2
import numpy as np

class AdaptiveISP:
    """
    Adaptive ISP with:
    - CLAHE (Contrast Limited Adaptive Histogram Equalization)
    - Denoising
    - Brightness/contrast auto-adjustment
    - Fog/haze removal
    - Low-light enhancement
    """
    
    def __init__(self):
        """Initialize Adaptive ISP"""
        # CLAHE parameters
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        
        # Brightness thresholds
        self.DARK_THRESHOLD = 50  # Mean brightness below this = dark
        self.BRIGHT_THRESHOLD = 200  # Mean brightness above this = bright
        
        # Processing modes
        self.mode = 'AUTO'  # AUTO, DAY, NIGHT, FOG
        
        print("✅ Adaptive ISP initialized")
        print("   • CLAHE enhancement: ACTIVE")
        print("   • Auto brightness: ACTIVE")
        print("   • Denoising: ACTIVE")
        print("   • Fog removal: ACTIVE")
    
    def detect_lighting_condition(self, image):
        """
        Detect lighting condition from image
        
        Args:
            image: Input BGR image
        
        Returns:
            condition: 'DARK', 'NORMAL', 'BRIGHT', 'FOG'
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate mean brightness
        mean_brightness = np.mean(gray)
        
        # Calculate standard deviation (contrast)
        std_brightness = np.std(gray)
        
        # Detect fog (low contrast, medium brightness)
        if std_brightness < 30 and 80 < mean_brightness < 180:
            return 'FOG'
        
        # Detect darkness
        if mean_brightness < self.DARK_THRESHOLD:
            return 'DARK'
        
        # Detect brightness
        if mean_brightness > self.BRIGHT_THRESHOLD:
            return 'BRIGHT'
        
        return 'NORMAL'
    
    def enhance_low_light(self, image):
        """
        Enhance low-light images using CLAHE
        
        Args:
            image: Input BGR image
        
        Returns:
            enhanced: Enhanced image
        """
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # Split channels
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        l_clahe = self.clahe.apply(l)
        
        # Merge channels
        lab_clahe = cv2.merge([l_clahe, a, b])
        
        # Convert back to BGR
        enhanced = cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2BGR)
        
        return enhanced
    
    def remove_fog(self, image):
        """
        Remove fog/haze using dark channel prior
        
        Args:
            image: Input BGR image
        
        Returns:
            dehazed: Dehazed image
        """
        # Simplified fog removal using contrast enhancement
        # Full dark channel prior is computationally expensive
        
        # Convert to LAB
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Enhance contrast
        l_enhanced = cv2.equalizeHist(l)
        
        # Merge and convert back
        lab_enhanced = cv2.merge([l_enhanced, a, b])
        dehazed = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
        
        # Increase saturation
        hsv = cv2.cvtColor(dehazed, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        s = cv2.add(s, 30)  # Increase saturation
        hsv_enhanced = cv2.merge([h, s, v])
        dehazed = cv2.cvtColor(hsv_enhanced, cv2.COLOR_HSV2BGR)
        
        return dehazed
    
    def adjust_brightness_contrast(self, image, brightness=0, contrast=0):
        """
        Adjust brightness and contrast
        
        Args:
            image: Input BGR image
            brightness: Brightness adjustment (-100 to 100)
            contrast: Contrast adjustment (-100 to 100)
        
        Returns:
            adjusted: Adjusted image
        """
        # Brightness adjustment
        if brightness != 0:
            if brightness > 0:
                shadow = brightness
                highlight = 255
            else:
                shadow = 0
                highlight = 255 + brightness
            alpha_b = (highlight - shadow) / 255
            gamma_b = shadow
            
            image = cv2.addWeighted(image, alpha_b, image, 0, gamma_b)
        
        # Contrast adjustment
        if contrast != 0:
            f = 131 * (contrast + 127) / (127 * (131 - contrast))
            alpha_c = f
            gamma_c = 127 * (1 - f)
            
            image = cv2.addWeighted(image, alpha_c, image, 0, gamma_c)
        
        return image
    
    def denoise(self, image):
        """
        Apply denoising
        
        Args:
            image: Input BGR image
        
        Returns:
            denoised: Denoised image
        """
        # Fast denoising
        denoised = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        return denoised
    
    def process(self, image, apply_denoising=False):
        """
        Main ISP pipeline
        
        Args:
            image: Input BGR image
            apply_denoising: Whether to apply denoising (slow)
        
        Returns:
            processed: Processed image
            condition: Detected lighting condition
        """
        try:
            # Detect lighting condition
            condition = self.detect_lighting_condition(image)
            
            processed = image.copy()
            
            # Apply appropriate processing
            if condition == 'DARK':
                # Low-light enhancement
                processed = self.enhance_low_light(processed)
                processed = self.adjust_brightness_contrast(processed, brightness=20, contrast=10)
                
            elif condition == 'FOG':
                # Fog removal
                processed = self.remove_fog(processed)
                
            elif condition == 'BRIGHT':
                # Reduce brightness
                processed = self.adjust_brightness_contrast(processed, brightness=-10, contrast=5)
            
            # Optional denoising (computationally expensive)
            if apply_denoising and condition in ['DARK', 'FOG']:
                processed = self.denoise(processed)
            
            return processed, condition
            
        except Exception as e:
            print(f"Error in ISP: {e}")
            return image, 'ERROR'
    
    def get_enhancement_info(self, condition):
        """
        Get information about applied enhancements
        
        Args:
            condition: Detected lighting condition
        
        Returns:
            info: Dictionary with enhancement info
        """
        enhancements = {
            'DARK': 'Low-light enhancement (CLAHE + Brightness)',
            'FOG': 'Fog removal (Contrast + Saturation)',
            'BRIGHT': 'Brightness reduction',
            'NORMAL': 'No enhancement',
            'ERROR': 'Processing error'
        }
        
        return {
            'condition': condition,
            'enhancement': enhancements.get(condition, 'Unknown'),
            'active': condition != 'NORMAL'
        }
