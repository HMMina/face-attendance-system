@echo off
echo =========================================
echo  Auto Download AI Models for Face System
echo =========================================
echo.

echo [1/5] Kiểm tra Python environment...
cd /d "%~dp0..\backend"

if not exist "venv" (
    echo 📦 Tạo virtual environment...
    python -m venv venv
)

echo 🔧 Kích hoạt virtual environment...
call venv\Scripts\activate.bat

echo.
echo [2/5] Cài đặt AI dependencies...
echo 📦 Installing Ultralytics (YOLO)...
pip install ultralytics>=8.0.0

echo 📦 Installing InsightFace...
pip install insightface>=0.7.0

echo 📦 Installing ONNX Runtime...
pip install onnxruntime>=1.15.0

echo 📦 Installing scikit-learn...
pip install scikit-learn>=1.3.0

echo ✅ AI dependencies installed

echo.
echo [3/5] Tạo thư mục models...
if not exist "data\models\detection" mkdir data\models\detection
if not exist "data\models\classification" mkdir data\models\classification  
if not exist "data\models\recognition" mkdir data\models\recognition

echo ✅ Model directories created

echo.
echo [4/5] Download AI models...

echo 🔍 Downloading YOLOv11s for face detection...
python -c "from ultralytics import YOLO; model = YOLO('yolov11s.pt'); print('YOLOv11s downloaded')"

echo 🛡️ Downloading YOLOv11s-cls for anti-spoofing...
python -c "from ultralytics import YOLO; model = YOLO('yolov11s-cls.pt'); print('YOLOv11s-cls downloaded')"

echo 🎯 Downloading InsightFace models...
python -c "import insightface; app = insightface.app.FaceAnalysis(name='buffalo_l'); app.prepare(ctx_id=0); print('InsightFace buffalo_l downloaded')"

echo.
echo [5/5] Copy models to project structure...

echo 📁 Copying YOLOv11s...
copy "%USERPROFILE%\.cache\ultralytics\yolov11s.pt" "data\models\detection\yolov11s.pt" >nul 2>&1
if not exist "data\models\detection\yolov11s.pt" (
    echo ⚠️ YOLOv11s not found in cache, will auto-download when needed
) else (
    echo ✅ YOLOv11s copied successfully
)

echo 📁 Copying YOLOv11s-cls...
copy "%USERPROFILE%\.cache\ultralytics\yolov11s-cls.pt" "data\models\classification\yolov11s-cls.pt" >nul 2>&1
if not exist "data\models\classification\yolov11s-cls.pt" (
    echo ⚠️ YOLOv11s-cls not found in cache, will auto-download when needed
) else (
    echo ✅ YOLOv11s-cls copied successfully
)

echo 📁 Copying InsightFace models...
if exist "%USERPROFILE%\.insightface\models\buffalo_l" (
    xcopy "%USERPROFILE%\.insightface\models\buffalo_l" "data\models\recognition\buffalo_l\" /E /I /Y >nul 2>&1
    echo ✅ InsightFace buffalo_l copied successfully
) else (
    echo ⚠️ InsightFace models not found, will auto-download when needed
)

echo.
echo =========================================
echo  ✅ Model Setup Complete!
echo =========================================
echo.
echo 📁 Model locations:
echo   Detection: data\models\detection\yolov11s.pt
echo   Anti-spoof: data\models\classification\yolov11s-cls.pt  
echo   Recognition: data\models\recognition\buffalo_l\
echo.
echo 🚀 Ready to start the system!
echo   Run: scripts\start_admin.bat
echo.
echo ℹ️ Models will auto-download on first use if not found
echo.

pause
