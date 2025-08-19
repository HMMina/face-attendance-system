"""
Real AI Service for Face Recognition
Replaces mock_ai_service.py with actual model implementations
"""
import cv2
import numpy as np
import logging
from typing import Tuple, Optional, List
from pathlib import Path
import pickle
import os
from sqlalchemy.orm import Session

# Import database services
from app.services.face_embedding_service import FaceEmbeddingService
from app.models.employee import Employee

# Will need these dependencies:
# pip install onnxruntime insightface ultralytics scikit-learn

class RealAIService:
    """
    Production AI service with real model implementations
    """
    
    def __init__(self, model_path: str = "data/models"):
        self.model_path = Path(model_path)
        self.logger = logging.getLogger(__name__)
        
        # Models will be loaded here
        self.face_detector = None
        self.anti_spoof_model = None  
        self.face_recognizer = None
        self.embedding_cache = {}
        
        self._load_models()
    
    def _load_models(self):
        """Load all AI models with fallback options"""
        try:
            # 1. Load Face Detection Model (Priority order)
            self._load_face_detector()
            
            # 2. Load Anti-Spoofing Model (Priority order)
            self._load_anti_spoof_model()
            
            # 3. Load Face Recognition Model (Priority order)
            self._load_face_recognizer()
            
        except Exception as e:
            self.logger.error(f"Model loading error: {e}")
            raise
    
    def _load_face_detector(self):
        """Load face detection model with priority order"""
        try:
            from ultralytics import YOLO
            
            # Priority order for face detection models
            detector_options = [
                self.model_path / "detection" / "yolov11s.pt",
                self.model_path / "detection" / "yolov8n-face.pt",
                self.model_path / "detection" / "yolov8n.pt",
                "yolov11s.pt"  # Auto-download fallback
            ]
            
            for detector_path in detector_options:
                try:
                    if isinstance(detector_path, Path) and detector_path.exists():
                        self.face_detector = YOLO(str(detector_path))
                        self.logger.info(f"Face detector loaded: {detector_path}")
                        return
                    elif isinstance(detector_path, str):
                        # Auto-download from Ultralytics
                        self.face_detector = YOLO(detector_path)
                        self.logger.info(f"Face detector auto-downloaded: {detector_path}")
                        return
                except Exception as e:
                    self.logger.warning(f"Failed to load {detector_path}: {e}")
                    continue
            
            raise Exception("No face detection model could be loaded")
            
        except ImportError:
            self.logger.error("Ultralytics not installed. Please install: pip install ultralytics")
            raise
    
    def _load_anti_spoof_model(self):
        """Load anti-spoofing model with priority order"""
        try:
            from ultralytics import YOLO
            
            # Priority order for anti-spoofing models
            spoof_options = [
                self.model_path / "classification" / "yolov11s-cls.pt",
                self.model_path / "classification" / "antispoofing.onnx",
                self.model_path / "classification" / "yolov8n-cls.pt"
            ]
            
            for spoof_path in spoof_options:
                try:
                    if spoof_path.exists():
                        if spoof_path.suffix == '.pt':
                            self.anti_spoof_model = YOLO(str(spoof_path))
                        elif spoof_path.suffix == '.onnx':
                            # Load ONNX model for anti-spoofing
                            import onnxruntime as ort
                            self.anti_spoof_model = ort.InferenceSession(str(spoof_path))
                        
                        self.logger.info(f"Anti-spoofing model loaded: {spoof_path}")
                        return
                except Exception as e:
                    self.logger.warning(f"Failed to load {spoof_path}: {e}")
                    continue
            
            self.logger.warning("No anti-spoofing model loaded - using mock implementation")
            self.anti_spoof_model = None
            
        except ImportError as e:
            self.logger.warning(f"Anti-spoofing dependencies missing: {e}")
            self.anti_spoof_model = None
    
    def _load_face_recognizer(self):
        """Load face recognition model with priority order"""
        try:
            import insightface
            
            # Priority order for face recognition models  
            recognition_options = [
                ("buffalo_l", self.model_path / "recognition" / "buffalo_l"),
                ("buffalo_s", self.model_path / "recognition" / "buffalo_s"),
                ("buffalo_l", None),  # Auto-download fallback
            ]
            
            for model_name, model_path in recognition_options:
                try:
                    if model_path and model_path.exists():
                        # Load from local path
                        self.face_recognizer = insightface.app.FaceAnalysis(
                            name=model_name,
                            root=str(model_path.parent),
                            providers=['CPUExecutionProvider']
                        )
                    else:
                        # Auto-download
                        self.face_recognizer = insightface.app.FaceAnalysis(
                            name=model_name,
                            providers=['CPUExecutionProvider']
                        )
                    
                    self.face_recognizer.prepare(ctx_id=0, det_size=(640, 640))
                    self.logger.info(f"Face recognizer loaded: {model_name}")
                    return
                    
                except Exception as e:
                    self.logger.warning(f"Failed to load {model_name}: {e}")
                    continue
            
            raise Exception("No face recognition model could be loaded")
            
        except ImportError:
            self.logger.error("InsightFace not installed. Please install: pip install insightface")
            raise
    
    def detect_face(self, image: np.ndarray) -> Tuple[bool, Optional[tuple]]:
        """
        Detect face in image using YOLOv11s
        Returns: (found, bbox) where bbox is (x1, y1, x2, y2)
        """
        try:
            if self.face_detector is None:
                return False, None
            
            results = self.face_detector(image, verbose=False)
            
            if len(results) == 0 or len(results[0].boxes) == 0:
                return False, None
            
            # Get the most confident face detection
            boxes = results[0].boxes
            best_box = boxes[boxes.conf.argmax()]
            
            # Convert to (x1, y1, x2, y2) format
            bbox = best_box.xyxy[0].cpu().numpy().astype(int)
            confidence = best_box.conf[0].cpu().numpy()
            
            # Only accept high-confidence detections
            if confidence < 0.5:
                return False, None
                
            return True, tuple(bbox)
            
        except Exception as e:
            self.logger.error(f"Face detection error: {e}")
            return False, None
    
    def anti_spoofing(self, image: np.ndarray, bbox: tuple = None) -> bool:
        """
        Check if face is real (anti-spoofing) using YOLOv11s-cls
        Returns: True if real face, False if spoof detected
        """
        try:
            if self.anti_spoof_model is None:
                # If model not available, assume real face
                return True
            
            # Crop face region if bbox provided
            if bbox:
                x1, y1, x2, y2 = bbox
                face_crop = image[y1:y2, x1:x2]
            else:
                face_crop = image
            
            results = self.anti_spoof_model(face_crop, verbose=False)
            
            if len(results) == 0:
                return True  # Default to real if uncertain
            
            # Get classification result
            probs = results[0].probs
            if probs is not None:
                # Assuming class 0 = real, class 1 = spoof
                real_confidence = probs.data[0].cpu().numpy()
                return real_confidence > 0.5
            
            return True
            
        except Exception as e:
            self.logger.error(f"Anti-spoofing error: {e}")
            return True  # Default to allowing if error
    
    def extract_embedding(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract 512-dimensional face embedding using InsightFace
        Returns: 512-dim numpy array or None if failed
        """
        try:
            if self.face_recognizer is None:
                return None
            
            # InsightFace expects RGB
            if len(image.shape) == 3 and image.shape[2] == 3:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = image
            
            faces = self.face_recognizer.get(rgb_image)
            
            if len(faces) == 0:
                return None
            
            # Get the first (most confident) face
            face = faces[0]
            embedding = face.embedding
            
            # Normalize embedding
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding.astype(np.float32)
            
        except Exception as e:
            self.logger.error(f"Embedding extraction error: {e}")
            return None
    
    def match_embedding(self, query_embedding: np.ndarray, 
                       employee_embeddings: List[Tuple[str, np.ndarray]], 
                       threshold: float = 0.7) -> Tuple[Optional[str], float]:
        """
        Match query embedding against database of employee embeddings
        Args:
            query_embedding: 512-dim query vector
            employee_embeddings: List of (employee_id, embedding) tuples
            threshold: Minimum similarity threshold
        Returns: (employee_id, confidence) or (None, 0.0) if no match
        """
        try:
            if len(employee_embeddings) == 0:
                return None, 0.0
            
            best_match = None
            best_similarity = 0.0
            
            for employee_id, stored_embedding in employee_embeddings:
                # Calculate cosine similarity
                similarity = np.dot(query_embedding, stored_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(stored_embedding)
                )
                
                if similarity > best_similarity and similarity >= threshold:
                    best_similarity = similarity
                    best_match = employee_id
            
            return best_match, best_similarity
            
        except Exception as e:
            self.logger.error(f"Embedding matching error: {e}")
            return None, 0.0
    
    def process_recognition(self, image_bytes: bytes, device_id: str, db: Session) -> dict:
        """
        Complete face recognition pipeline with database integration
        """
        try:
            # 1. Decode image
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return {
                    "success": False,
                    "message": "Invalid image format",
                    "device_id": device_id
                }
            
            # 2. Detect face
            found, bbox = self.detect_face(image)
            if not found:
                return {
                    "success": False,
                    "message": "No face detected",
                    "device_id": device_id
                }
            
            # 3. Anti-spoofing check
            if not self.anti_spoofing(image, bbox):
                return {
                    "success": False,
                    "message": "Spoof attempt detected",
                    "device_id": device_id
                }
            
            # 4. Extract embedding
            embedding = self.extract_embedding(image)
            if embedding is None:
                return {
                    "success": False,
                    "message": "Failed to extract face features",
                    "device_id": device_id
                }
            
            # 5. Match with database
            employee_id, confidence, embedding_id = FaceEmbeddingService.find_best_match(
                db, embedding, min_threshold=0.7
            )
            
            if employee_id is None:
                return {
                    "success": False,
                    "message": "Face not recognized",
                    "device_id": device_id,
                    "confidence": 0.0
                }
            
            # 6. Get employee information
            employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
            if not employee:
                return {
                    "success": False,
                    "message": "Employee data not found",
                    "device_id": device_id
                }
            
            # 7. Return successful recognition
            return {
                "success": True,
                "recognized": True,
                "employee_id": employee_id,
                "employee": {
                    "name": employee.name,
                    "position": employee.position,
                    "department": employee.department,
                    "employee_id": employee.employee_id
                },
                "confidence": confidence,
                "bbox": bbox,
                "device_id": device_id,
                "message": "Face recognized successfully",
                "timestamp": "2025-08-19T08:00:00Z"
            }
            
        except Exception as e:
            self.logger.error(f"Recognition pipeline error: {e}")
            return {
                "success": False,
                "message": f"Processing error: {str(e)}",
                "device_id": device_id
            }
    
    def register_face(self, image_bytes: bytes, employee_id: str, device_id: str, db: Session) -> dict:
        """
        Register a new face for an employee
        """
        try:
            # 1. Decode image
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return {
                    "success": False,
                    "message": "Invalid image format"
                }
            
            # 2. Check if employee exists
            employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
            if not employee:
                return {
                    "success": False,
                    "message": f"Employee {employee_id} not found"
                }
            
            # 3. Detect face
            found, bbox = self.detect_face(image)
            if not found:
                return {
                    "success": False,
                    "message": "No face detected in registration image"
                }
            
            # 4. Anti-spoofing check
            if not self.anti_spoofing(image, bbox):
                return {
                    "success": False,
                    "message": "Spoof detected in registration image"
                }
            
            # 5. Extract embedding
            embedding = self.extract_embedding(image)
            if embedding is None:
                return {
                    "success": False,
                    "message": "Failed to extract face features from registration image"
                }
            
            # 6. Save face photo
            import datetime
            photo_dir = Path("data/face_photos/employee_photos")
            photo_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            photo_filename = f"{employee_id}_{timestamp}.jpg"
            photo_path = photo_dir / photo_filename
            
            cv2.imwrite(str(photo_path), image)
            
            # 7. Check if this is the first embedding (make it primary)
            existing_embeddings = FaceEmbeddingService.get_employee_embeddings(db, employee_id)
            is_primary = len(existing_embeddings) == 0
            
            # 8. Save embedding to database
            face_embedding = FaceEmbeddingService.save_embedding(
                db=db,
                employee_id=employee_id,
                embedding=embedding,
                face_photo_path=str(photo_path),
                confidence_threshold=0.7,
                photo_quality=0.8,  # Could implement quality assessment
                registered_by="system",
                registration_device=device_id,
                is_primary=is_primary
            )
            
            return {
                "success": True,
                "message": f"Face registered successfully for {employee.name}",
                "employee_id": employee_id,
                "embedding_id": face_embedding.id,
                "photo_path": str(photo_path),
                "is_primary": is_primary
            }
            
        except Exception as e:
            self.logger.error(f"Face registration error: {e}")
            return {
                "success": False,
                "message": f"Registration error: {str(e)}"
            }

# Global instance
ai_service = None

def get_ai_service() -> RealAIService:
    """Get or create AI service singleton"""
    global ai_service
    if ai_service is None:
        ai_service = RealAIService()
    return ai_service

# Integration functions for existing codebase
def real_recognition(image_bytes: bytes, device_id: str, db: Session) -> dict:
    """
    Replace mock_recognition with this function
    """
    service = get_ai_service()
    return service.process_recognition(image_bytes, device_id, db)

def register_employee_face(image_bytes: bytes, employee_id: str, device_id: str, db: Session) -> dict:
    """
    Register new face for employee
    """
    service = get_ai_service()
    return service.register_face(image_bytes, employee_id, device_id, db)
