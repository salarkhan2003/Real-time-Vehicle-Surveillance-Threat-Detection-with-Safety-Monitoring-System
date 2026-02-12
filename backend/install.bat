@echo off
echo Installing Python dependencies for YOLOv8 backend...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.
echo Installation complete!
echo Run 'python server.py' to start the detection server
pause
