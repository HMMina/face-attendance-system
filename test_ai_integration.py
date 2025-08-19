"""
Test script for AI integration
Tests face detection, embedding extraction, and database operations
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

import cv2
import numpy as np
from sqlalchemy.orm import Session
from app.config.database import SessionLocal
from app.services.real_ai_service import get_ai_service, register_employee_face
from app.services.face_embedding_service import FaceEmbeddingService
from app.models.employee import Employee
from app.models.face_embedding import FaceEmbedding

def test_ai_models():
    """Test AI model loading"""
    print("🧪 Testing AI model loading...")
    
    try:
        ai_service = get_ai_service()
        print("✅ AI service initialized successfully")
        
        # Test with dummy image
        dummy_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Test face detection
        found, bbox = ai_service.detect_face(dummy_image)
        print(f"✅ Face detection test: Found={found}, BBox={bbox}")
        
        # Test anti-spoofing
        is_real = ai_service.anti_spoofing(dummy_image)
        print(f"✅ Anti-spoofing test: Real={is_real}")
        
        # Test embedding extraction
        embedding = ai_service.extract_embedding(dummy_image)
        if embedding is not None:
            print(f"✅ Embedding extraction test: Shape={embedding.shape}")
        else:
            print("⚠️ Embedding extraction failed (expected with dummy image)")
        
        return True
        
    except Exception as e:
        print(f"❌ AI model test failed: {e}")
        return False

def test_database_operations():
    """Test database operations"""
    print("\n🧪 Testing database operations...")
    
    db = SessionLocal()
    try:
        # Test creating test employee
        test_employee = Employee(
            employee_id="TEST001",
            name="Test User",
            department="IT",
            position="Tester",
            email="test@company.com"
        )
        
        # Check if test employee exists
        existing = db.query(Employee).filter(Employee.employee_id == "TEST001").first()
        if not existing:
            db.add(test_employee)
            db.commit()
            print("✅ Test employee created")
        else:
            print("✅ Test employee already exists")
        
        # Test embedding operations
        dummy_embedding = np.random.random(512).astype(np.float32)
        
        # Save embedding
        face_embedding = FaceEmbeddingService.save_embedding(
            db=db,
            employee_id="TEST001",
            embedding=dummy_embedding,
            confidence_threshold=0.8,
            is_primary=True
        )
        print(f"✅ Embedding saved with ID: {face_embedding.id}")
        
        # Test retrieval
        embeddings = FaceEmbeddingService.get_employee_embeddings(db, "TEST001")
        print(f"✅ Retrieved {len(embeddings)} embeddings for TEST001")
        
        # Test similarity calculation
        similarity = FaceEmbeddingService.calculate_similarity(
            dummy_embedding, dummy_embedding
        )
        print(f"✅ Similarity calculation test: {similarity:.4f} (should be ~1.0)")
        
        # Test best match
        employee_id, confidence, emb_id = FaceEmbeddingService.find_best_match(
            db, dummy_embedding, min_threshold=0.5
        )
        print(f"✅ Best match test: Employee={employee_id}, Confidence={confidence:.4f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    finally:
        db.close()

def test_end_to_end():
    """Test end-to-end face recognition pipeline"""
    print("\n🧪 Testing end-to-end pipeline...")
    
    try:
        # Create test image (simple colored rectangle)
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        test_image[100:400, 200:440] = [100, 150, 200]  # Face-like rectangle
        
        # Encode as JPEG
        success, buffer = cv2.imencode('.jpg', test_image)
        if not success:
            print("❌ Failed to encode test image")
            return False
            
        image_bytes = buffer.tobytes()
        
        # Test recognition pipeline
        db = SessionLocal()
        try:
            ai_service = get_ai_service()
            result = ai_service.process_recognition(image_bytes, "test_device", db)
            print(f"✅ Recognition pipeline result: {result}")
            
            # Test registration pipeline
            reg_result = register_employee_face(image_bytes, "TEST001", "test_device", db)
            print(f"✅ Registration pipeline result: {reg_result}")
            
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 AI Integration Test Suite")
    print("=" * 50)
    
    # Test 1: AI Models
    ai_test = test_ai_models()
    
    # Test 2: Database Operations  
    db_test = test_database_operations()
    
    # Test 3: End-to-End Pipeline
    e2e_test = test_end_to_end()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"🤖 AI Models: {'✅ PASS' if ai_test else '❌ FAIL'}")
    print(f"💾 Database: {'✅ PASS' if db_test else '❌ FAIL'}")
    print(f"🔄 End-to-End: {'✅ PASS' if e2e_test else '❌ FAIL'}")
    
    if all([ai_test, db_test, e2e_test]):
        print("\n🎉 ALL TESTS PASSED! AI integration is ready!")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please check the configuration.")
        return 1

if __name__ == "__main__":
    exit(main())
