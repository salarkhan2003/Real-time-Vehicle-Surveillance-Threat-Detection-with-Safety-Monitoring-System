# 📡 API Documentation

## Overview

GuardVision AI provides a RESTful API for real-time object detection and fatigue monitoring. This document covers all available endpoints, request/response formats, and usage examples.

**Base URL:** `http://localhost:5000`

**API Version:** 2.0

---

## Table of Contents

1. [Authentication](#authentication)
2. [Endpoints](#endpoints)
3. [Request/Response Formats](#requestresponse-formats)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Code Examples](#code-examples)

---

## Authentication

### API Key (Optional)

For production deployments, API key authentication is recommended:

```http
Authorization: Bearer YOUR_API_KEY
```

**Example:**
```bash
curl -H "Authorization: Bearer abc123xyz" \
     http://localhost:5000/detect
```

---

## Endpoints

### 1. Health Check

Check if the server is running and models are loaded.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "ok",
  "model": "YOLOv8x",
  "version": "2.0"
}
```

**Example:**
```bash
curl http://localhost:5000/health
```

---

### 2. Object Detection & Fatigue Analysis

Main endpoint for processing images.

**Endpoint:** `POST /detect`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "modes": {
    "fatigue": true,
    "vehicle": true
  }
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image` | string | Yes | Base64-encoded image (JPEG/PNG) |
| `modes` | object | No | Detection modes (default: both enabled) |
| `modes.fatigue` | boolean | No | Enable fatigue detection |
| `modes.vehicle` | boolean | No | Enable vehicle/object detection |

**Response:**
```json
{
  "detections": [
    {
      "label": "person",
      "confidence": 0.92,
      "x": 245,
      "y": 120,
      "w": 180,
      "h": 420,
      "distance": 3.5,
      "alertLevel": "WARNING",
      "hasHelmet": null
    }
  ],
  "fatigue": 0.15,
  "fatigueDetails": {
    "faces_detected": 1,
    "eyes_detected": 2,
    "eye_state": "open",
    "status": "Alert - Eyes Open",
    "ear": 0.28,
    "mar": 0.35,
    "confidence": 0.95,
    "eyes_closed": false,
    "yawning": false,
    "blink_rate": 18
  },
  "speed": 0,
  "alertThresholds": {
    "critical": 2.0,
    "warning": 3.5,
    "safe": 5.0
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `detections` | array | List of detected objects |
| `detections[].label` | string | Object class (person, car, etc.) |
| `detections[].confidence` | float | Detection confidence (0.0-1.0) |
| `detections[].x` | int | X coordinate (normalized 0-1000) |
| `detections[].y` | int | Y coordinate (normalized 0-1000) |
| `detections[].w` | int | Width (normalized 0-1000) |
| `detections[].h` | int | Height (normalized 0-1000) |
| `detections[].distance` | float | Estimated distance (meters) |
| `detections[].alertLevel` | string | SAFE, WARNING, or CRITICAL |
| `detections[].hasHelmet` | boolean/null | Helmet detection (person only) |
| `fatigue` | float | Fatigue level (0.0-1.0) |
| `fatigueDetails` | object | Detailed fatigue metrics |
| `fatigueDetails.ear` | float | Eye Aspect Ratio |
| `fatigueDetails.mar` | float | Mouth Aspect Ratio |
| `fatigueDetails.blink_rate` | int | Blinks per minute |
| `speed` | float | Estimated speed (km/h) |
| `alertThresholds` | object | Distance thresholds |

**Example:**
```bash
curl -X POST http://localhost:5000/detect \
  -H "Content-Type: application/json" \
  -d '{
    "image": "data:image/jpeg;base64,/9j/4AAQ...",
    "modes": {
      "fatigue": true,
      "vehicle": true
    }
  }'
```

---

### 3. Model Information

Get information about loaded models.

**Endpoint:** `GET /model/info`

**Response:**
```json
{
  "yolo": {
    "model": "YOLOv8x",
    "size": "136MB",
    "mAP": "54%",
    "classes": 80,
    "parameters": "68.2M"
  },
  "fatigue": {
    "method": "MediaPipe Face Mesh",
    "landmarks": 468,
    "accuracy": "95%+",
    "features": ["EAR", "MAR", "Blink Rate"]
  }
}
```

---

### 4. System Metrics

Get system performance metrics.

**Endpoint:** `GET /metrics`

**Response:**
```json
{
  "inference_count": 1523,
  "average_inference_time": 0.125,
  "detections_total": 4567,
  "fatigue_alerts": 23,
  "uptime": 3600,
  "cpu_usage": 65.5,
  "memory_usage": 2048,
  "gpu_usage": 45.2
}
```

---

### 5. Configuration

Get or update system configuration.

**Endpoint:** `GET /config`

**Response:**
```json
{
  "confidence_threshold": 0.15,
  "iou_threshold": 0.40,
  "image_size": 1280,
  "max_detections": 300,
  "ear_threshold": 0.25,
  "mar_threshold": 0.6
}
```

**Endpoint:** `POST /config`

**Request Body:**
```json
{
  "confidence_threshold": 0.20,
  "image_size": 640
}
```

---

## Request/Response Formats

### Image Encoding

Images must be base64-encoded with data URI format:

```javascript
// JavaScript example
const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d');
ctx.drawImage(videoElement, 0, 0);
const base64Image = canvas.toDataURL('image/jpeg', 0.8);

// Send to API
fetch('http://localhost:5000/detect', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    image: base64Image,
    modes: { fatigue: true, vehicle: true }
  })
});
```

```python
# Python example
import base64
import cv2
import requests

# Read image
image = cv2.imread('image.jpg')
_, buffer = cv2.imencode('.jpg', image)
base64_image = base64.b64encode(buffer).decode('utf-8')

# Send to API
response = requests.post('http://localhost:5000/detect', json={
    'image': f'data:image/jpeg;base64,{base64_image}',
    'modes': {'fatigue': True, 'vehicle': True}
})

result = response.json()
```

### Coordinate System

Coordinates are normalized to 0-1000 range:

```
(0, 0) ────────────────── (1000, 0)
  │                            │
  │                            │
  │         (x, y)             │
  │           •                │
  │         w × h              │
  │                            │
(0, 1000) ────────────── (1000, 1000)
```

**Convert to pixels:**
```javascript
const pixelX = (x / 1000) * imageWidth;
const pixelY = (y / 1000) * imageHeight;
const pixelW = (w / 1000) * imageWidth;
const pixelH = (h / 1000) * imageHeight;
```

---

## Error Handling

### Error Response Format

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": "Additional details"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request format |
| 401 | Unauthorized | Missing or invalid API key |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Model not loaded |

### Common Errors

**1. No Image Provided**
```json
{
  "error": "No image provided",
  "code": "MISSING_IMAGE"
}
```

**2. Invalid Image Format**
```json
{
  "error": "Invalid image format",
  "code": "INVALID_IMAGE"
}
```

**3. Model Not Loaded**
```json
{
  "error": "Model not loaded",
  "code": "MODEL_ERROR"
}
```

**4. Rate Limit Exceeded**
```json
{
  "error": "Rate limit exceeded",
  "code": "RATE_LIMIT",
  "details": "10 requests per minute allowed"
}
```

---

## Rate Limiting

### Default Limits

- **Per IP:** 10 requests per minute
- **Per API Key:** 100 requests per minute
- **Burst:** 20 requests

### Rate Limit Headers

```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1640000000
```

### Handling Rate Limits

```javascript
async function detectWithRetry(image, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch('http://localhost:5000/detect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image, modes: { fatigue: true, vehicle: true } })
      });
      
      if (response.status === 429) {
        const resetTime = response.headers.get('X-RateLimit-Reset');
        const waitTime = (resetTime * 1000) - Date.now();
        await new Promise(resolve => setTimeout(resolve, waitTime));
        continue;
      }
      
      return await response.json();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
    }
  }
}
```

---

## Code Examples

### JavaScript/TypeScript

```typescript
interface DetectionRequest {
  image: string;
  modes: {
    fatigue: boolean;
    vehicle: boolean;
  };
}

interface DetectionResponse {
  detections: Detection[];
  fatigue: number;
  fatigueDetails: FatigueDetails;
  speed: number;
  alertThresholds: AlertThresholds;
}

async function runDetection(
  videoElement: HTMLVideoElement,
  modes: { fatigue: boolean; vehicle: boolean }
): Promise<DetectionResponse> {
  // Capture frame
  const canvas = document.createElement('canvas');
  canvas.width = videoElement.videoWidth;
  canvas.height = videoElement.videoHeight;
  
  const ctx = canvas.getContext('2d')!;
  ctx.drawImage(videoElement, 0, 0);
  
  // Convert to base64
  const base64Image = canvas.toDataURL('image/jpeg', 0.8);
  
  // Send request
  const response = await fetch('http://localhost:5000/detect', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer YOUR_API_KEY'
    },
    body: JSON.stringify({
      image: base64Image,
      modes
    })
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  
  return await response.json();
}

// Usage
const result = await runDetection(videoRef.current, {
  fatigue: true,
  vehicle: true
});

console.log('Detections:', result.detections);
console.log('Fatigue level:', result.fatigue);
```

### Python

```python
import cv2
import base64
import requests
import json
from typing import Dict, List

class GuardVisionClient:
    def __init__(self, base_url: str = 'http://localhost:5000', api_key: str = None):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })
    
    def detect(self, image, modes: Dict[str, bool] = None) -> Dict:
        """
        Run detection on image
        
        Args:
            image: numpy array (BGR) or file path
            modes: {'fatigue': bool, 'vehicle': bool}
        
        Returns:
            Detection results
        """
        # Read image if path provided
        if isinstance(image, str):
            image = cv2.imread(image)
        
        # Encode image
        _, buffer = cv2.imencode('.jpg', image)
        base64_image = base64.b64encode(buffer).decode('utf-8')
        
        # Prepare request
        payload = {
            'image': f'data:image/jpeg;base64,{base64_image}',
            'modes': modes or {'fatigue': True, 'vehicle': True}
        }
        
        # Send request
        response = self.session.post(
            f'{self.base_url}/detect',
            json=payload
        )
        
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict:
        """Check server health"""
        response = self.session.get(f'{self.base_url}/health')
        response.raise_for_status()
        return response.json()

# Usage
client = GuardVisionClient(api_key='YOUR_API_KEY')

# Check health
health = client.health_check()
print(f"Server status: {health['status']}")

# Run detection
cap = cv2.VideoCapture(0)
ret, frame = cap.read()

result = client.detect(frame, modes={'fatigue': True, 'vehicle': True})

print(f"Detections: {len(result['detections'])}")
print(f"Fatigue level: {result['fatigue']:.2f}")

for detection in result['detections']:
    print(f"  {detection['label']}: {detection['confidence']:.2f} at {detection['distance']:.1f}m")

cap.release()
```

### cURL

```bash
# Health check
curl http://localhost:5000/health

# Detection with both modes
curl -X POST http://localhost:5000/detect \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
    "modes": {
      "fatigue": true,
      "vehicle": true
    }
  }'

# Detection with fatigue only
curl -X POST http://localhost:5000/detect \
  -H "Content-Type: application/json" \
  -d '{
    "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
    "modes": {
      "fatigue": true,
      "vehicle": false
    }
  }'

# Get metrics
curl http://localhost:5000/metrics
```

### Node.js

```javascript
const axios = require('axios');
const fs = require('fs');

class GuardVisionClient {
  constructor(baseURL = 'http://localhost:5000', apiKey = null) {
    this.client = axios.create({
      baseURL,
      headers: apiKey ? { 'Authorization': `Bearer ${apiKey}` } : {}
    });
  }

  async detect(imagePath, modes = { fatigue: true, vehicle: true }) {
    // Read and encode image
    const imageBuffer = fs.readFileSync(imagePath);
    const base64Image = imageBuffer.toString('base64');
    
    // Send request
    const response = await this.client.post('/detect', {
      image: `data:image/jpeg;base64,${base64Image}`,
      modes
    });
    
    return response.data;
  }

  async healthCheck() {
    const response = await this.client.get('/health');
    return response.data;
  }
}

// Usage
(async () => {
  const client = new GuardVisionClient('http://localhost:5000', 'YOUR_API_KEY');
  
  // Health check
  const health = await client.healthCheck();
  console.log('Server status:', health.status);
  
  // Run detection
  const result = await client.detect('image.jpg', {
    fatigue: true,
    vehicle: true
  });
  
  console.log('Detections:', result.detections.length);
  console.log('Fatigue level:', result.fatigue);
})();
```

---

## WebSocket API (Real-Time)

For real-time streaming, WebSocket API is available:

```javascript
const ws = new WebSocket('ws://localhost:5000/stream');

ws.onopen = () => {
  console.log('Connected to GuardVision');
  
  // Send configuration
  ws.send(JSON.stringify({
    type: 'config',
    modes: { fatigue: true, vehicle: true }
  }));
};

ws.onmessage = (event) => {
  const result = JSON.parse(event.data);
  
  if (result.type === 'detection') {
    console.log('Detections:', result.detections);
    console.log('Fatigue:', result.fatigue);
  }
};

// Send frame
function sendFrame(videoElement) {
  const canvas = document.createElement('canvas');
  canvas.width = videoElement.videoWidth;
  canvas.height = videoElement.videoHeight;
  
  const ctx = canvas.getContext('2d');
  ctx.drawImage(videoElement, 0, 0);
  
  const base64Image = canvas.toDataURL('image/jpeg', 0.8);
  
  ws.send(JSON.stringify({
    type: 'frame',
    image: base64Image
  }));
}

// Send frames at 2 FPS
setInterval(() => sendFrame(videoRef.current), 500);
```

---

## Best Practices

### 1. Image Quality
- Use JPEG format with 80% quality
- Recommended resolution: 640×480 to 1280×720
- Ensure good lighting conditions

### 2. Request Frequency
- Recommended: 2 FPS (500ms interval)
- Maximum: 4 FPS (250ms interval)
- Avoid exceeding rate limits

### 3. Error Handling
- Always check HTTP status codes
- Implement retry logic with exponential backoff
- Handle rate limit errors gracefully

### 4. Performance
- Reuse HTTP connections
- Compress images before encoding
- Use WebSocket for real-time streaming

### 5. Security
- Always use HTTPS in production
- Store API keys securely
- Implement request signing
- Validate responses

---

## Support

For API support:
- Documentation: See COMPLETE_TECHNICAL_REPORT.md
- Issues: GitHub Issues
- Email: support@guardvision.ai

---

**API Version:** 2.0  
**Last Updated:** 2024  
**Status:** Production Ready ✅
