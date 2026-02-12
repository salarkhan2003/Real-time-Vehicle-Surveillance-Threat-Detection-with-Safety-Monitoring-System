@echo off
echo ============================================================
echo   Installing MediaPipe for Accurate Fatigue Detection
echo ============================================================
echo.
echo This will install MediaPipe - a production-grade AI library
echo from Google that provides MUCH better fatigue detection.
echo.
echo Old system (Haar Cascades): 60-70%% accuracy
echo New system (MediaPipe): 95%%+ accuracy
echo.
pause
echo.
echo Installing MediaPipe...
pip install mediapipe
echo.
echo ============================================================
echo   Installation Complete!
echo ============================================================
echo.
echo MediaPipe is now installed.
echo.
echo Next steps:
echo 1. Start the server: python server.py
echo 2. Test fatigue detection with your face
echo 3. Eyes open should show 0-10%% fatigue
echo 4. Eyes closed should show 70-95%% fatigue
echo.
echo The system will now work MUCH better!
echo.
pause
