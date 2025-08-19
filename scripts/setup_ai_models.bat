@echo off
REM 🚀 Windows AI Model Setup Script
REM Downloads required AI models for face recognition

echo 🤖 Setting up AI models for Face Recognition System...

REM Create model directories
if not exist "data\models\detection" mkdir data\models\detection
if not exist "data\models\classification" mkdir data\models\classification  
if not exist "data\models\recognition" mkdir data\models\recognition
if not exist "data\face_photos\employee_photos" mkdir data\face_photos\employee_photos
if not exist "data\face_photos\daily_captures" mkdir data\face_photos\daily_captures
if not exist "data\face_photos\temp" mkdir data\face_photos\temp
if not exist "data\embeddings\cache" mkdir data\embeddings\cache
if not exist "data\embeddings\backups" mkdir data\embeddings\backups

echo 📁 Model directories created

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python first.
    pause
    exit /b 1
)

echo 📥 Installing AI dependencies...
pip install -r requirements_ai.txt

echo 📥 Downloading AI models...

REM Download YOLOv11s for face detection
echo 📥 Setting up YOLO models...
cd data\models\detection

python -c "from ultralytics import YOLO; model = YOLO('yolov11s.pt'); print('YOLOv11s downloaded successfully')"

cd ..\classification

python -c "from ultralytics import YOLO; model = YOLO('yolov11s-cls.pt'); print('YOLOv11s-cls downloaded successfully')"

REM Setup InsightFace models
echo 📥 Setting up InsightFace models...
cd ..\recognition

python -c "import insightface; app = insightface.app.FaceAnalysis(providers=['CPUExecutionProvider']); app.prepare(ctx_id=0, det_size=(640, 640)); print('InsightFace models prepared successfully')"

cd ..\..\..

echo ✅ All AI models downloaded successfully!
echo.
echo 📊 Model Information:
echo - Face Detection: YOLOv11s (~22MB)
echo - Anti-Spoofing: YOLOv11s-cls (~22MB)
echo - Face Recognition: InsightFace ArcFace (~100MB)
echo.
echo 🎯 Ready for AI integration!
echo.
echo 🔧 Next steps:
echo 1. Run database migration: alembic upgrade head
echo 2. Set USE_REAL_AI=true in .env file
echo 3. Start the server: python start_server.py
echo.
pause
