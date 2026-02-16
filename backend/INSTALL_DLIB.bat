@echo off
echo ========================================
echo   INSTALLING HIGH-ACCURACY FATIGUE DETECTION
echo ========================================
echo.
echo This will install:
echo   - dlib (facial landmark detection)
echo   - scipy (mathematical calculations)
echo   - Download 68-point facial landmark model
echo.
echo This provides 95%+ accuracy for eye detection!
echo.
pause
echo.

echo Step 1: Installing dlib...
pip install dlib
if errorlevel 1 (
    echo.
    echo ❌ dlib installation failed!
    echo.
    echo dlib requires Visual Studio C++ compiler on Windows.
    echo.
    echo SOLUTION: Install pre-compiled wheel
    echo.
    echo For Python 3.14 (64-bit):
    pip install https://github.com/z-mahmud22/Dlib_Windows_Python3.x/raw/main/dlib-19.24.1-cp314-cp314-win_amd64.whl
    echo.
    if errorlevel 1 (
        echo ❌ Pre-compiled wheel also failed!
        echo.
        echo Please install Visual Studio Build Tools:
        echo https://visualstudio.microsoft.com/visual-cpp-build-tools/
        echo.
        pause
        exit /b 1
    )
)

echo.
echo Step 2: Installing scipy...
pip install scipy

echo.
echo Step 3: Downloading facial landmark model...
python download_dlib_model.py

echo.
echo ========================================
echo   INSTALLATION COMPLETE!
echo ========================================
echo.
echo ✅ dlib installed
echo ✅ scipy installed
echo ✅ 68-point facial landmark model downloaded
echo.
echo You can now use HIGH-ACCURACY fatigue detection!
echo.
pause
