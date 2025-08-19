#!/bin/bash
# 🚀 AI Model Download Script
# Downloads required AI models for face recognition

echo "🤖 Setting up AI models for Face Recognition System..."

# Create model directories
mkdir -p data/models/detection
mkdir -p data/models/classification  
mkdir -p data/models/recognition
mkdir -p data/face_photos/employee_photos
mkdir -p data/face_photos/daily_captures
mkdir -p data/face_photos/temp
mkdir -p data/embeddings/cache
mkdir -p data/embeddings/backups

echo "📁 Model directories created"

# Download YOLOv11s for face detection
echo "📥 Downloading YOLOv11s face detection model..."
cd data/models/detection

# Method 1: Using ultralytics (will auto-download)
python3 -c "
from ultralytics import YOLO
model = YOLO('yolov11s.pt')  # This will download automatically
print('YOLOv11s downloaded successfully')
"

# Download YOLOv11s-cls for anti-spoofing classification
echo "📥 Downloading YOLOv11s classification model..."
cd ../classification

python3 -c "
from ultralytics import YOLO
model = YOLO('yolov11s-cls.pt')  # Classification model
print('YOLOv11s-cls downloaded successfully')
"

# Setup InsightFace models
echo "📥 Setting up InsightFace models..."
cd ../recognition

python3 -c "
import insightface
# This will download models automatically on first use
app = insightface.app.FaceAnalysis(providers=['CPUExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 640))
print('InsightFace models prepared successfully')
"

echo "✅ All AI models downloaded successfully!"
echo ""
echo "📊 Model Information:"
echo "- Face Detection: YOLOv11s (~22MB)"
echo "- Anti-Spoofing: YOLOv11s-cls (~22MB)" 
echo "- Face Recognition: InsightFace ArcFace (~100MB)"
echo ""
echo "🎯 Ready for AI integration!"
