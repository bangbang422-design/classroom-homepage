@echo off
echo Starting Classroom App...
cd /d "%~dp0"
echo Current folder: %CD%

echo.
echo Installing required packages...
pip install flask flask-socketio eventlet werkzeug

echo.
echo Starting "우리반 ON" classroom application...
echo.
echo Open your browser and go to: http://localhost:5000
echo.
echo Test accounts:
echo Teacher: username=teacher, password=teacher123
echo Student: username=student1, password=student123
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause