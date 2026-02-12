# Quick Reference Card

## 🚀 Start System
```bash
cd backend && python server.py    # Terminal 1
npm run dev                        # Terminal 2
```

## 🎛️ Mode Selection
- **Both ON** → Full monitoring (100% resources)
- **Fatigue Only** → Driver monitoring (30% resources)
- **Vehicle Only** → Object detection (80% resources)
- **Both OFF** → Standby (5% resources)

## 🎯 Fatigue Detection
- **0-15%** = Alert (eyes open) ✅
- **60-70%** = Drowsy (eyes closing) ⚠️
- **85-95%** = Sleeping (eyes closed) 🚨

## 🚨 Emergency Alerts
- **Fatigue Mode ON** → Shows "FATIGUE DETECTED" only
- **Vehicle Mode ON** → Shows "OBJECT IN BLIND SPOT" only
- **Both ON** → Shows both if both triggered
- **Mode OFF** → No alert for that mode

## 📚 Documentation
- **USER_GUIDE.md** - Complete guide
- **QUICKSTART.md** - Quick start
- **TECHNICAL_REPORT.md** - Technical details
- **FINAL_FIXES_APPLIED.md** - Latest fixes

## 🐛 Troubleshooting
- **Backend error** → `pip install -r requirements.txt`
- **Frontend error** → `npm install`
- **Fatigue wrong** → Restart server
- **Alerts wrong** → Restart server

## ✅ System Ready!
All fixes applied. Start and test now! 🚀
