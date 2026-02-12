@echo off
echo ======================================================================
echo   Downloading YOLOv8 Medium Model for High Accuracy Detection
echo ======================================================================
echo.
echo This will download YOLOv8m model (~50MB)
echo.
echo Press any key to start download...
pause > nul
echo.
echo Downloading...
echo.

python download_yolov8m.py

echo.
echo ======================================================================
echo   Download Complete!
echo ======================================================================
echo.
echo Next steps:
echo   1. Run: START_SERVER.bat
echo   2. Open new terminal and run: npm run dev
echo   3. Test high-accuracy detection
echo.
pause
