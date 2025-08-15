"""
Mock AI service for face recognition
"""
"""
Pipeline xử lý AI nhận diện khuôn mặt (mock cho MVP)
Các bước: detect, anti-spoof, extract embedding, so khớp
"""
import random

def detect_face(image):
    # Mock YOLOv11s: phát hiện khuôn mặt
    return True, (100, 100, 200, 200)  # found, bbox

def anti_spoofing(image):
    # Mock YOLOv11s-cls: kiểm tra giả mạo
    return True  # real face

def extract_embedding(image):
    # Mock InsightFace: trích xuất embedding
    return [random.random() for _ in range(512)]

def match_embedding(embedding):
    # Mock so khớp với database
    # Trả về employee_id nếu khớp
    return "E123", 0.98

def mock_recognition(image, device_id):
    # Pipeline xử lý ảnh
    found, bbox = detect_face(image)
    if not found:
        return {"recognized": False, "msg": "Không tìm thấy khuôn mặt"}
    if not anti_spoofing(image):
        return {"recognized": False, "msg": "Phát hiện giả mạo"}
    embedding = extract_embedding(image)
    employee_id, confidence = match_embedding(embedding)
    # (Mock) Lưu embedding vào database nếu cần
    return {
        "device_id": device_id,
        "recognized": True,
        "employee_id": employee_id,
        "confidence": confidence,
        "bbox": bbox,
        "timestamp": "2025-08-13T08:00:00Z"
    }
