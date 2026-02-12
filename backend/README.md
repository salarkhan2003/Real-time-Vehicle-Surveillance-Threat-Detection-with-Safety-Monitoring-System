# YOLOv8 Detection Backend

High-accuracy object detection server using YOLOv8 for real-time monitoring.

## Setup

### Windows

1. Install Python 3.8+ from https://www.python.org/downloads/
2. Run `install.bat` to install dependencies
3. Start server: `python server.py`

### Manual Installation

```bash
cd backend
pip install -r requirements.txt
python server.py
```

## Features

- Real-time object detection with YOLOv8
- Detects: person, car, truck, motorcycle, bicycle, and 75+ other objects
- High accuracy (>90% for common objects)
- Fast inference (~50-100ms per frame)
- Automatic distance estimation
- REST API endpoint at http://localhost:5000

## API Endpoints

### POST /detect
Detects objects in an image

Request:
```json
{
  "image": "base64_encoded_image"
}
```

Response:
```json
{
  "detections": [
    {
      "label": "person",
      "confidence": 0.95,
      "x": 100,
      "y": 150,
      "w": 200,
      "h": 400,
      "distance": 3.0,
      "hasHelmet": false
    }
  ],
  "fatigue": 0.1,
  "speed": 0
}
```

### GET /health
Check server status

## Model Options

- `yolov8n.pt` - Nano (fastest, ~6MB)
- `yolov8s.pt` - Small (balanced)
- `yolov8m.pt` - Medium (more accurate)
- `yolov8l.pt` - Large (best accuracy)
- `yolov8x.pt` - Extra Large (highest accuracy)

Edit `server.py` line 11 to change model.

## Troubleshooting

If you get "Model not found", the first run will automatically download YOLOv8 weights (~6MB).

For GPU acceleration, install CUDA and use:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```
