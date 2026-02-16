"""
Visualization Module
Draw lanes, detection boxes, and ADAS overlays on camera feed
"""

import cv2
import numpy as np

def draw_lane_lines(image, lka_data):
    """
    Draw detected lane lines on image
    
    Args:
        image: BGR image
        lka_data: Lane detection data with polynomial fits
    
    Returns:
        image: Image with lane lines drawn
    """
    if not lka_data or not lka_data.get('detected'):
        return image
    
    try:
        left_fit = np.array(lka_data.get('left_fit', []))
        right_fit = np.array(lka_data.get('right_fit', []))
        
        if len(left_fit) == 0 or len(right_fit) == 0:
            return image
        
        h, w = image.shape[:2]
        
        # Generate points for lane lines
        ploty = np.linspace(0, h-1, h)
        
        # Calculate x positions using polynomial: x = Ay² + By + C
        left_fitx = left_fit[0] * ploty**2 + left_fit[1] * ploty + left_fit[2]
        right_fitx = right_fit[0] * ploty**2 + right_fit[1] * ploty + right_fit[2]
        
        # Create lane overlay
        lane_overlay = np.zeros_like(image)
        
        # Draw filled polygon between lanes
        pts_left = np.array([np.transpose(np.vstack([left_fitx, ploty]))])
        pts_right = np.array([np.flipud(np.transpose(np.vstack([right_fitx, ploty])))])
        pts = np.hstack((pts_left, pts_right))
        
        # Fill lane area with semi-transparent green
        cv2.fillPoly(lane_overlay, np.int32([pts]), (0, 255, 0))
        
        # Draw lane lines
        for i in range(len(ploty) - 1):
            # Left lane line (yellow)
            if 0 <= left_fitx[i] < w and 0 <= left_fitx[i+1] < w:
                cv2.line(image, 
                        (int(left_fitx[i]), int(ploty[i])),
                        (int(left_fitx[i+1]), int(ploty[i+1])),
                        (0, 255, 255), 8)  # Yellow
            
            # Right lane line (yellow)
            if 0 <= right_fitx[i] < w and 0 <= right_fitx[i+1] < w:
                cv2.line(image, 
                        (int(right_fitx[i]), int(ploty[i])),
                        (int(right_fitx[i+1]), int(ploty[i+1])),
                        (0, 255, 255), 8)  # Yellow
        
        # Blend lane overlay with original image
        image = cv2.addWeighted(image, 1, lane_overlay, 0.3, 0)
        
        # Draw lane info text
        offset = lka_data.get('offset', 0)
        status = lka_data.get('status', 'Unknown')
        departure = lka_data.get('departure_warning', False)
        
        # Text background
        cv2.rectangle(image, (10, 10), (400, 100), (0, 0, 0), -1)
        cv2.rectangle(image, (10, 10), (400, 100), (0, 255, 255), 2)
        
        # Status text
        color = (0, 0, 255) if departure else (0, 255, 0)
        cv2.putText(image, f"LKA: {status}", (20, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(image, f"Offset: {offset:.2f}m", (20, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
    except Exception as e:
        print(f"⚠️  Lane drawing error: {e}")
    
    return image


def draw_detection_boxes(image, detections):
    """
    Draw high-quality detection boxes with labels
    
    Args:
        image: BGR image
        detections: List of detection dictionaries
    
    Returns:
        image: Image with detection boxes drawn
    """
    h, w = image.shape[:2]
    
    for det in detections:
        try:
            # Get bbox in pixels
            bbox = det.get('bbox', [])
            if len(bbox) != 4:
                continue
            
            x1, y1, box_w, box_h = bbox
            x2 = x1 + box_w
            y2 = y1 + box_h
            
            # Ensure coordinates are within image bounds
            x1 = max(0, min(int(x1), w-1))
            y1 = max(0, min(int(y1), h-1))
            x2 = max(0, min(int(x2), w-1))
            y2 = max(0, min(int(y2), h-1))
            
            # Get detection info
            label = det.get('label', 'unknown')
            confidence = det.get('confidence', 0)
            distance = det.get('distance', 0)
            alert_level = det.get('alertLevel', 'SAFE')
            
            # Color based on alert level
            if alert_level == 'CRITICAL':
                color = (0, 0, 255)  # Red
                thickness = 4
            elif alert_level == 'WARNING':
                color = (0, 165, 255)  # Orange
                thickness = 3
            else:
                color = (0, 255, 0)  # Green
                thickness = 2
            
            # Draw main box
            cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)
            
            # Draw corner markers for better visibility
            corner_length = 20
            # Top-left
            cv2.line(image, (x1, y1), (x1 + corner_length, y1), color, thickness + 2)
            cv2.line(image, (x1, y1), (x1, y1 + corner_length), color, thickness + 2)
            # Top-right
            cv2.line(image, (x2, y1), (x2 - corner_length, y1), color, thickness + 2)
            cv2.line(image, (x2, y1), (x2, y1 + corner_length), color, thickness + 2)
            # Bottom-left
            cv2.line(image, (x1, y2), (x1 + corner_length, y2), color, thickness + 2)
            cv2.line(image, (x1, y2), (x1, y2 - corner_length), color, thickness + 2)
            # Bottom-right
            cv2.line(image, (x2, y2), (x2 - corner_length, y2), color, thickness + 2)
            cv2.line(image, (x2, y2), (x2, y2 - corner_length), color, thickness + 2)
            
            # Prepare label text
            label_text = f"{label.upper()}"
            conf_text = f"{confidence*100:.0f}%"
            dist_text = f"{distance:.1f}m"
            
            # Calculate text size
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            font_thickness = 2
            
            (label_w, label_h), _ = cv2.getTextSize(label_text, font, font_scale, font_thickness)
            (conf_w, conf_h), _ = cv2.getTextSize(conf_text, font, font_scale - 0.1, font_thickness - 1)
            (dist_w, dist_h), _ = cv2.getTextSize(dist_text, font, font_scale - 0.1, font_thickness - 1)
            
            # Draw label background
            label_bg_h = label_h + conf_h + 20
            label_bg_w = max(label_w, conf_w, dist_w) + 20
            
            # Position label above box if possible, otherwise below
            if y1 - label_bg_h - 5 > 0:
                label_y = y1 - label_bg_h - 5
            else:
                label_y = y2 + 5
            
            # Draw semi-transparent background
            overlay = image.copy()
            cv2.rectangle(overlay, (x1, label_y), (x1 + label_bg_w, label_y + label_bg_h), color, -1)
            cv2.addWeighted(overlay, 0.7, image, 0.3, 0, image)
            
            # Draw border
            cv2.rectangle(image, (x1, label_y), (x1 + label_bg_w, label_y + label_bg_h), color, 2)
            
            # Draw text
            cv2.putText(image, label_text, (x1 + 10, label_y + label_h + 5),
                       font, font_scale, (255, 255, 255), font_thickness)
            cv2.putText(image, conf_text, (x1 + 10, label_y + label_h + conf_h + 10),
                       font, font_scale - 0.1, (255, 255, 255), font_thickness - 1)
            cv2.putText(image, dist_text, (x1 + 10, label_y + label_h + conf_h + dist_h + 15),
                       font, font_scale - 0.1, (255, 255, 255), font_thickness - 1)
            
            # Draw distance line from bottom center of box
            center_x = (x1 + x2) // 2
            cv2.line(image, (center_x, y2), (center_x, y2 + 30), color, 2)
            cv2.circle(image, (center_x, y2 + 30), 5, color, -1)
            
        except Exception as e:
            print(f"⚠️  Box drawing error: {e}")
            continue
    
    return image


def add_adas_hud(image, lka_data, tsr_data, intent_data, isp_data):
    """
    Add ADAS HUD overlay with all feature status
    
    Args:
        image: BGR image
        lka_data: Lane Keep Assist data
        tsr_data: Traffic Sign Recognition data
        intent_data: Pedestrian Intent data
        isp_data: Adaptive ISP data
    
    Returns:
        image: Image with HUD overlay
    """
    h, w = image.shape[:2]
    
    # HUD background (top-right corner)
    hud_x = w - 350
    hud_y = 10
    hud_w = 340
    hud_h = 200
    
    # Semi-transparent background
    overlay = image.copy()
    cv2.rectangle(overlay, (hud_x, hud_y), (hud_x + hud_w, hud_y + hud_h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, image, 0.4, 0, image)
    
    # Border
    cv2.rectangle(image, (hud_x, hud_y), (hud_x + hud_w, hud_y + hud_h), (0, 255, 255), 2)
    
    # Title
    cv2.putText(image, "ADAS STATUS", (hud_x + 10, hud_y + 25),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    y_offset = hud_y + 50
    
    # LKA Status
    if lka_data and lka_data.get('detected'):
        status = lka_data.get('status', 'N/A')
        color = (0, 0, 255) if lka_data.get('departure_warning') else (0, 255, 0)
        cv2.putText(image, f"LKA: {status}", (hud_x + 10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        y_offset += 25
    
    # TSR Status
    if tsr_data and tsr_data.get('signs_detected', 0) > 0:
        signs = tsr_data.get('signs_detected', 0)
        color = (0, 0, 255) if tsr_data.get('speed_warning') else (0, 255, 0)
        cv2.putText(image, f"TSR: {signs} signs", (hud_x + 10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        y_offset += 25
    
    # Pedestrian Intent
    if intent_data and len(intent_data) > 0:
        warnings = sum(1 for p in intent_data if p.get('warning'))
        color = (0, 0, 255) if warnings > 0 else (0, 255, 0)
        cv2.putText(image, f"INTENT: {len(intent_data)} tracked", (hud_x + 10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        y_offset += 25
    
    # ISP Status
    if isp_data and isp_data.get('active'):
        condition = isp_data.get('condition', 'N/A')
        cv2.putText(image, f"ISP: {condition}", (hud_x + 10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (138, 43, 226), 1)
        y_offset += 25
    
    return image
