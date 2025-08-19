#!/usr/bin/env python3
"""
Test script để kiểm tra AI models đã setup đúng chưa
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

def test_model_files():
    """Kiểm tra model files có tồn tại không"""
    print("🔍 Checking model files...")
    
    model_path = backend_path / "data" / "models"
    
    # Required model files
    required_models = [
        "detection/yolov11s.pt",
        "classification/yolov11s-cls.pt", 
        "recognition/buffalo_l"
    ]
    
    all_found = True
    for model in required_models:
        model_file = model_path / model
        if model_file.exists():
            print(f"✅ Found: {model}")
        else:
            print(f"❌ Missing: {model}")
            all_found = False
    
    return all_found

def test_dependencies():
    """Kiểm tra AI dependencies"""
    print("\n🔧 Checking AI dependencies...")
    
    dependencies = [
        ("ultralytics", "YOLO models"),
        ("insightface", "Face recognition"),
        ("onnxruntime", "ONNX models"),
        ("cv2", "OpenCV"),
        ("numpy", "NumPy")
    ]
    
    all_installed = True
    for dep, desc in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}: {desc}")
        except ImportError:
            print(f"❌ {dep}: {desc} - NOT INSTALLED")
            all_installed = False
    
    return all_installed

def test_ai_service():
    """Test AI service initialization"""
    print("\n🤖 Testing AI Service...")
    
    try:
        from app.services.real_ai_service import RealAIService
        
        # Initialize service
        ai_service = RealAIService()
        
        # Check components
        components = [
            ("face_detector", "Face Detection"),
            ("anti_spoof_model", "Anti-Spoofing"),
            ("face_recognizer", "Face Recognition")
        ]
        
        all_loaded = True
        for attr, name in components:
            if hasattr(ai_service, attr) and getattr(ai_service, attr) is not None:
                print(f"✅ {name}: Loaded")
            else:
                print(f"❌ {name}: Not loaded")
                all_loaded = False
        
        return all_loaded
        
    except Exception as e:
        print(f"❌ AI Service initialization failed: {e}")
        return False

def test_sample_processing():
    """Test với ảnh mẫu"""
    print("\n📷 Testing sample image processing...")
    
    try:
        import cv2
        import numpy as np
        from app.services.real_ai_service import RealAIService
        
        # Tạo ảnh test đơn giản
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        test_image[100:380, 200:440] = [100, 150, 200]  # Face-like rectangle
        
        ai_service = RealAIService()
        
        # Test face detection
        face_found, bbox = ai_service.detect_face(test_image)
        print(f"Face Detection: {'✅ Found face' if face_found else '❌ No face detected'}")
        
        if face_found:
            # Test anti-spoofing
            is_real = ai_service.anti_spoofing(test_image, bbox)
            print(f"Anti-Spoofing: {'✅ Real face' if is_real else '⚠️ Possible spoof'}")
            
            # Test embedding extraction
            embedding = ai_service.extract_embedding(test_image, bbox)
            if embedding is not None:
                print(f"✅ Embedding extracted: {len(embedding)} dimensions")
            else:
                print("❌ Embedding extraction failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Sample processing failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 AI Models Test Suite")
    print("=" * 50)
    
    # Run all tests
    tests = [
        ("Model Files", test_model_files),
        ("Dependencies", test_dependencies), 
        ("AI Service", test_ai_service),
        ("Sample Processing", test_sample_processing)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} : {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! AI system is ready to use.")
        print("\n🚀 Next steps:")
        print("1. Run: scripts/start_admin.bat")
        print("2. Open: http://localhost:8000/admin")
        print("3. Upload employee photos and test!")
    else:
        print("⚠️ SOME TESTS FAILED! Please check the issues above.")
        print("\n🔧 Troubleshooting:")
        print("1. Run: scripts/download_models.bat")
        print("2. Install missing dependencies")
        print("3. Check model file locations")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
