#!/bin/bash

echo "========================================="
echo " Auto Download AI Models for Face System"
echo "========================================="
echo

echo "[1/5] Checking Python environment..."
cd "$(dirname "$0")/../backend"

if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo
echo "[2/5] Installing AI dependencies..."
echo "📦 Installing Ultralytics (YOLO)..."
pip install ultralytics>=8.0.0

echo "📦 Installing InsightFace..."
pip install insightface>=0.7.0

echo "📦 Installing ONNX Runtime..."
pip install onnxruntime>=1.15.0

echo "📦 Installing scikit-learn..."
pip install scikit-learn>=1.3.0

echo "✅ AI dependencies installed"

echo
echo "[3/5] Creating model directories..."
mkdir -p data/models/detection
mkdir -p data/models/classification  
mkdir -p data/models/recognition

echo "✅ Model directories created"

echo
echo "[4/5] Downloading AI models..."

echo "🔍 Downloading YOLOv11s for face detection..."
python -c "from ultralytics import YOLO; model = YOLO('yolov11s.pt'); print('YOLOv11s downloaded')"

echo "🛡️ Downloading YOLOv11s-cls for anti-spoofing..."
python -c "from ultralytics import YOLO; model = YOLO('yolov11s-cls.pt'); print('YOLOv11s-cls downloaded')"

echo "🎯 Downloading InsightFace models..."
python -c "import insightface; app = insightface.app.FaceAnalysis(name='buffalo_l'); app.prepare(ctx_id=0); print('InsightFace buffalo_l downloaded')"

echo
echo "[5/5] Copying models to project structure..."

echo "📁 Copying YOLOv11s..."
if [ -f "$HOME/.cache/ultralytics/yolov11s.pt" ]; then
    cp "$HOME/.cache/ultralytics/yolov11s.pt" "data/models/detection/yolov11s.pt"
    echo "✅ YOLOv11s copied successfully"
else
    echo "⚠️ YOLOv11s not found in cache, will auto-download when needed"
fi

echo "📁 Copying YOLOv11s-cls..."
if [ -f "$HOME/.cache/ultralytics/yolov11s-cls.pt" ]; then
    cp "$HOME/.cache/ultralytics/yolov11s-cls.pt" "data/models/classification/yolov11s-cls.pt"
    echo "✅ YOLOv11s-cls copied successfully"
else
    echo "⚠️ YOLOv11s-cls not found in cache, will auto-download when needed"
fi

echo "📁 Copying InsightFace models..."
if [ -d "$HOME/.insightface/models/buffalo_l" ]; then
    cp -r "$HOME/.insightface/models/buffalo_l" "data/models/recognition/"
    echo "✅ InsightFace buffalo_l copied successfully"
else
    echo "⚠️ InsightFace models not found, will auto-download when needed"
fi

echo
echo "========================================="
echo " ✅ Model Setup Complete!"
echo "========================================="
echo
echo "📁 Model locations:"
echo "   Detection: data/models/detection/yolov11s.pt"
echo "   Anti-spoof: data/models/classification/yolov11s-cls.pt"  
echo "   Recognition: data/models/recognition/buffalo_l/"
echo
echo "🚀 Ready to start the system!"
echo "   Run: ./scripts/start_admin.sh"
echo
echo "ℹ️ Models will auto-download on first use if not found"
echo
