#!/usr/bin/env python3
"""
Optimized AI Models Test Suite
Comprehensive testing for Face Attendance System AI models
"""
import sys
import os
import time
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_section(title):
    """Print formatted section"""
    print(f"\n📋 {title}:")
    print("-" * 40)

def check_model_files():
    """Enhanced model files checking"""
    print_section("Model Files Verification")
    
    model_path = backend_path / "data" / "models"
    if not model_path.exists():
        print("❌ Model directory not found!")
        return False
    
    print(f"📁 Model path: {model_path}")
    
    # Required models with expected sizes
    required_models = {
        "detection/yolov11s.pt": (15, 25),  # 15-25 MB
        "classification/yolov11s-cls.pt": (8, 15),  # 8-15 MB
        "recognition/buffalo_l": None  # Directory
    }
    
    all_found = True
    total_size = 0
    
    for model_rel_path, size_range in required_models.items():
        model_file = model_path / model_rel_path
        
        if model_file.exists():
            if model_file.is_file():
                size_mb = model_file.stat().st_size / (1024*1024)
                total_size += size_mb
                
                if size_range and (size_mb < size_range[0] or size_mb > size_range[1]):
                    print(f"⚠️  {model_rel_path}: {size_mb:.1f}MB (expected {size_range[0]}-{size_range[1]}MB)")
                else:
                    print(f"✅ {model_rel_path}: {size_mb:.1f}MB")
            else:
                # Directory check
                files = list(model_file.glob("*.onnx"))
                dir_size = sum(f.stat().st_size for f in files) / (1024*1024)
                total_size += dir_size
                print(f"✅ {model_rel_path}/: {len(files)} files, {dir_size:.1f}MB")
        else:
            print(f"❌ Missing: {model_rel_path}")
            all_found = False
    
    print(f"\n📊 Total models size: {total_size:.1f}MB")
    return all_found

def check_dependencies():
    """Enhanced dependencies checking"""
    print_section("AI Dependencies Verification")
    
    critical_deps = {
        "ultralytics": "YOLO models (Critical)",
        "insightface": "Face recognition (Critical)",
        "cv2": "OpenCV (Critical)",
        "numpy": "NumPy (Critical)"
    }
    
    optional_deps = {
        "onnxruntime": "ONNX models (Optional)",
        "psutil": "System monitoring (Optional)",
        "torch": "PyTorch backend (Recommended)"
    }
    
    all_critical = True
    
    print("Critical Dependencies:")
    for dep, desc in critical_deps.items():
        try:
            __import__(dep)
            print(f"  ✅ {dep}: {desc}")
        except ImportError:
            print(f"  ❌ {dep}: {desc} - NOT INSTALLED")
            all_critical = False
    
    print("\nOptional Dependencies:")
    for dep, desc in optional_deps.items():
        try:
            module = __import__(dep)
            version = getattr(module, '__version__', 'unknown')
            print(f"  ✅ {dep} v{version}: {desc}")
        except ImportError:
            print(f"  ⚠️  {dep}: {desc} - not installed")
    
    return all_critical

def test_ai_service_initialization():
    """Enhanced AI service testing"""
    print_section("AI Service Initialization")
    
    try:
        from app.services.real_ai_service import RealAIService
        
        print("🚀 Initializing AI Service...")
        start_time = time.time()
        
        ai_service = RealAIService()
        
        init_time = time.time() - start_time
        print(f"⏱️  Initialization time: {init_time:.2f}s")
        
        # Get model info
        model_info = ai_service.get_model_info()
        
        print("\n🔍 Model Status:")
        for model_type, info in model_info.get("models_loaded", {}).items():
            status = info.get("status", "unknown")
            model_name = info.get("type", "unknown")
            if status == "loaded":
                print(f"  ✅ {model_type}: {model_name}")
            else:
                print(f"  ❌ {model_type}: {status}")
        
        # System info
        if "system_info" in model_info:
            sys_info = model_info["system_info"]
            print(f"\n💻 System: {sys_info.get('platform', 'unknown')}")
            print(f"🧠 CPU cores: {sys_info.get('cpu_count', 'unknown')}")
            print(f"💾 Memory: {sys_info.get('memory_gb', 'unknown')}GB")
        
        return ai_service, True
        
    except Exception as e:
        print(f"❌ AI Service initialization failed: {e}")
        return None, False

def test_face_processing_pipeline(ai_service):
    """Test face processing with various image types"""
    print_section("Face Processing Pipeline")
    
    try:
        import cv2
        import numpy as np
        
        # Test cases with different image scenarios
        test_cases = [
            ("Small image", (160, 120)),
            ("Medium image", (640, 480)),
            ("Large image", (1280, 720)),
            ("Portrait image", (480, 640)),
        ]
        
        results = {}
        
        for test_name, (width, height) in test_cases:
            print(f"\n🧪 Testing {test_name} ({width}x{height})...")
            
            # Create test image with face-like region
            test_image = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
            
            # Add a simple face-like rectangle (for basic detection test)
            face_size = min(width, height) // 3
            x_center, y_center = width // 2, height // 2
            x1 = max(0, x_center - face_size // 2)
            y1 = max(0, y_center - face_size // 2)
            x2 = min(width, x1 + face_size)
            y2 = min(height, y1 + face_size)
            
            # Make face region brighter (skin-like color)
            test_image[y1:y2, x1:x2] = [200, 180, 160]
            
            start_time = time.time()
            
            # Test face detection
            face_found, bbox = ai_service.detect_face(test_image)
            detection_time = time.time() - start_time
            
            embedding_time = 0
            embedding_success = False
            
            if face_found:
                start_time = time.time()
                embedding = ai_service.extract_embedding(test_image)
                embedding_time = time.time() - start_time
                embedding_success = embedding is not None
                
                print(f"  ✅ Face detected: {bbox}")
                if embedding_success:
                    print(f"  ✅ Embedding extracted: {len(embedding)} dimensions")
                else:
                    print(f"  ⚠️  Embedding extraction failed")
            else:
                print(f"  ⚠️  No face detected")
            
            results[test_name] = {
                "face_detected": face_found,
                "embedding_extracted": embedding_success,
                "detection_time_ms": round(detection_time * 1000, 2),
                "embedding_time_ms": round(embedding_time * 1000, 2),
                "total_time_ms": round((detection_time + embedding_time) * 1000, 2)
            }
        
        # Performance summary
        print(f"\n📊 Performance Summary:")
        for test_name, result in results.items():
            print(f"  {test_name}: {result['total_time_ms']}ms total")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline testing failed: {e}")
        return False

def test_admin_upload_workflow(ai_service):
    """Test admin upload workflow specifically"""
    print_section("Admin Upload Workflow")
    
    try:
        import asyncio
        import numpy as np
        
        # Create a more realistic test image
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Add background
        test_image[:] = [240, 240, 240]  # Light gray background
        
        # Add face-like oval
        center_x, center_y = 320, 240
        face_width, face_height = 160, 200
        
        # Simple face simulation
        for y in range(max(0, center_y - face_height//2), min(480, center_y + face_height//2)):
            for x in range(max(0, center_x - face_width//2), min(640, center_x + face_width//2)):
                # Ellipse equation
                dx = (x - center_x) / (face_width // 2)
                dy = (y - center_y) / (face_height // 2)
                if dx*dx + dy*dy <= 1:
                    test_image[y, x] = [220, 190, 170]  # Skin color
        
        # Convert to bytes (simulate upload)
        import cv2
        _, image_bytes = cv2.imencode('.jpg', test_image)
        image_bytes = image_bytes.tobytes()
        
        print(f"🖼️  Test image: 640x480, {len(image_bytes)} bytes")
        
        # Test async processing
        async def test_async():
            result = await ai_service.process_recognition(image_bytes)
            return result
        
        # Run async test
        start_time = time.time()
        result = asyncio.run(test_async())
        processing_time = time.time() - start_time
        
        print(f"⏱️  Processing time: {processing_time:.2f}s")
        print(f"🎯 Result: {result.get('message', 'No message')}")
        
        # Analyze result
        if result.get('success'):
            print(f"  ✅ Face detected: {result.get('face_detected')}")
            print(f"  ✅ Real face: {result.get('is_real')}")
            print(f"  ✅ Quality score: {result.get('face_quality', 0):.2f}")
            print(f"  ✅ Embedding length: {len(result.get('embedding', []))}")
            return True
        else:
            print(f"  ⚠️  Processing failed: {result.get('message')}")
            return False
        
    except Exception as e:
        print(f"❌ Admin workflow test failed: {e}")
        return False

def generate_performance_report(results):
    """Generate comprehensive performance report"""
    print_header("PERFORMANCE REPORT")
    
    # Calculate overall score
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    score = (passed_tests / total_tests) * 100
    
    # Status summary
    print(f"📊 Overall Score: {score:.1f}% ({passed_tests}/{total_tests} tests passed)")
    
    if score >= 90:
        status = "🟢 EXCELLENT"
        recommendations = ["System is production-ready!", "Consider GPU acceleration for better performance."]
    elif score >= 75:
        status = "🟡 GOOD"
        recommendations = ["System is functional with minor issues.", "Check failed tests and optimize."]
    elif score >= 50:
        status = "🟠 MODERATE"
        recommendations = ["System has significant issues.", "Review failed components.", "Consider reinstalling dependencies."]
    else:
        status = "🔴 POOR"
        recommendations = ["System is not ready for production.", "Multiple critical failures detected.", "Full system review required."]
    
    print(f"🏆 Status: {status}")
    
    print(f"\n📋 Test Results:")
    for test_name, passed in results.items():
        icon = "✅" if passed else "❌"
        print(f"  {icon} {test_name}")
    
    print(f"\n💡 Recommendations:")
    for rec in recommendations:
        print(f"  • {rec}")
    
    # Next steps
    print(f"\n🚀 Next Steps:")
    if score >= 75:
        print("  1. Start the admin dashboard: scripts/start_admin.bat")
        print("  2. Open: http://localhost:8000/admin")
        print("  3. Upload employee photos and test!")
    else:
        print("  1. Fix failed tests above")
        print("  2. Run: scripts/download_models.bat")
        print("  3. Check model files and dependencies")
        print("  4. Re-run this test script")

def main():
    """Main test execution"""
    print_header("🤖 AI MODELS OPTIMIZATION TEST SUITE")
    print(f"📅 Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🗂️  Backend Path: {backend_path}")
    
    results = {}
    
    # Run all tests
    results["Model Files"] = check_model_files()
    results["Dependencies"] = check_dependencies()
    
    ai_service, service_ok = test_ai_service_initialization()
    results["AI Service Init"] = service_ok
    
    if service_ok:
        results["Face Processing"] = test_face_processing_pipeline(ai_service)
        results["Admin Upload"] = test_admin_upload_workflow(ai_service)
    else:
        results["Face Processing"] = False
        results["Admin Upload"] = False
    
    # Generate final report
    generate_performance_report(results)

if __name__ == "__main__":
    main()
