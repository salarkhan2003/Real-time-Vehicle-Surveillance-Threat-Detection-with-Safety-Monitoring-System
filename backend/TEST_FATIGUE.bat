@echo off
echo ========================================
echo   FATIGUE DETECTION TEST
echo ========================================
echo.
echo This will test fatigue detection with your webcam
echo.
echo INSTRUCTIONS:
echo   - Look at the camera normally
echo   - Close your eyes to test drowsiness
echo   - Press 'q' to quit
echo.
pause
echo.
echo Starting test...
python test_fatigue_live.py
pause
