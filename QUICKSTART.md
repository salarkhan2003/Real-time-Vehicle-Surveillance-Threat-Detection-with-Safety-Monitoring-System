# 🚀 Quick Start Guide

## Step-by-Step Setup

### 1️⃣ Install Python Backend

Open a terminal and run:

```bash
cd backend
```

**Windows:**
```bash
install.bat
```

**Linux/Mac:**
```bash
pip install -r requirements.txt
```

This will install:
- Flask (web server)
- YOLOv8 (object detection)
- OpenCV (image processing)
- Other dependencies

⏱️ Takes 2-5 minutes depending on your internet speed.

---

### 2️⃣ Start YOLOv8 Detection Server

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
python server.py
```

You should see:
```
Starting YOLOv8 Detection Server...
Model loaded successfully!
* Running on http://0.0.0.0:5000
```

✅ Keep this terminal open!

---

### 3️⃣ Start Frontend Dashboard

Open a NEW terminal and run:

```bash
npm run dev
```

You should see:
```
VITE v6.4.1  ready in 640 ms
➜  Local:   http://localhost:3000/
```

---

### 4️⃣ Open Dashboard

Open your browser and go to:
```
http://localhost:3000
```

---

## 🎮 Using the Dashboard

1. Click **"ACTIVATE NEURAL OPTICS"** to start monitoring
2. Allow camera access when prompted
3. The system will detect objects in real-time
4. Green boxes = detected objects
5. Red alerts = safety violations

---

## 🔍 What Gets Detected?

YOLOv8 detects 80+ objects including:

✅ **People** - person  
✅ **Vehicles** - car, truck, bus, motorcycle, bicycle  
✅ **Animals** - dog, cat, horse, bird, cow, etc.  
✅ **Objects** - backpack, umbrella, handbag, bottle, etc.

---

## ⚙️ Adjusting Settings

### Change Detection Speed

Edit `App.tsx` line 244:
```typescript
const timer = setInterval(runInference, 2000); // 2 seconds
```

- Lower = faster detection (more CPU usage)
- Higher = slower detection (less CPU usage)

### Change Model Accuracy

Edit `backend/server.py` line 11:
```python
model = YOLO('yolov8n.pt')  # Fast
# model = YOLO('yolov8m.pt')  # Balanced
# model = YOLO('yolov8l.pt')  # Accurate
```

### Change Confidence Threshold

Edit `backend/server.py` line 28:
```python
results = model(image_np, conf=0.5, iou=0.45, verbose=False)
#                          ^^^^ Lower = more detections
```

---

## 🐛 Common Issues

### "YOLO BACKEND OFFLINE"
- Backend server is not running
- Start it with `python backend/server.py`

### "Module not found"
- Dependencies not installed
- Run `pip install -r requirements.txt` in backend folder

### Camera not working
- Check browser permissions
- Try a different browser (Chrome recommended)
- Check if another app is using the camera

### Slow detection
- Use a smaller model (yolov8n.pt)
- Increase detection interval (3000-5000ms)
- Close other applications

---

## 🎯 Next Steps

- Adjust detection threshold for your use case
- Try different YOLOv8 models for accuracy vs speed
- Add custom object classes
- Deploy to production server

---

**Need Help?** Check the main README.md or backend/README.md for more details.
