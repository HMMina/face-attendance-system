"""
Face Recognition Service using Local Photos
Compares camera input with stored local employee photos
"""
import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging
from app.services.employee_photo_service import photo_service
from app.services.real_ai_service import RealAIService
from app.services.face_embedding_service import FaceEmbeddingService
from app.services.employee_service import EmployeeService
from app.config.database import get_db

logger = logging.getLogger(__name__)

class FaceRecognitionService:
    """Service for face recognition using local stored photos"""
    
    def __init__(self):
        self.ai_service = RealAIService()
        self.similarity_threshold = 0.6  # Threshold for face matching
        logger.info("FaceRecognitionService initialized")
    
    async def recognize_face_from_camera(self, camera_image: np.ndarray, db_session) -> Dict[str, any]:
        """
        Recognize face from camera input by comparing with local stored photos
        
        Args:
            camera_image: Image from camera as numpy array
            db_session: Database session
            
        Returns:
            Recognition result with employee info
        """
        try:
            # Extract face embedding from camera image
            camera_result = await self.ai_service.process_recognition(camera_image)
            
            if not camera_result.get("face_detected"):
                return {
                    "recognized": False,
                    "reason": "No face detected in camera image",
                    "confidence": 0.0
                }
            
            if not camera_result.get("is_real"):
                return {
                    "recognized": False,
                    "reason": "Spoof detected - not a real face",
                    "confidence": 0.0
                }
            
            camera_embedding = camera_result.get("embedding")
            if camera_embedding is None:
                return {
                    "recognized": False,
                    "reason": "Failed to extract face embedding",
                    "confidence": 0.0
                }
            
            # Get all employees with stored photos
            storage_stats = photo_service.get_storage_stats()
            if storage_stats.get("total_employees", 0) == 0:
                return {
                    "recognized": False,
                    "reason": "No employee photos stored in system",
                    "confidence": 0.0
                }
            
            # Find best match by comparing with all stored photos
            best_match = await self._find_best_match(camera_embedding, db_session)
            
            if best_match and best_match["similarity"] >= self.similarity_threshold:
                # Get employee details
                employee_service = EmployeeService()
                employee = employee_service.get_employee(db_session, best_match["employee_id"])
                
                return {
                    "recognized": True,
                    "employee": {
                        "employee_id": employee.employee_id,
                        "name": employee.name,
                        "department": employee.department,
                        "position": employee.position,
                        "email": employee.email
                    },
                    "confidence": best_match["similarity"],
                    "matched_photo": best_match["photo_path"],
                    "processing_time": camera_result.get("processing_time", 0.0),
                    "face_quality": camera_result.get("face_quality", 0.0)
                }
            else:
                return {
                    "recognized": False,
                    "reason": f"No matching employee found (best similarity: {best_match['similarity']:.2f})" if best_match else "No face comparisons possible",
                    "confidence": best_match["similarity"] if best_match else 0.0,
                    "threshold": self.similarity_threshold
                }
                
        except Exception as e:
            logger.error(f"Error in face recognition: {e}")
            return {
                "recognized": False,
                "reason": f"Recognition error: {str(e)}",
                "confidence": 0.0
            }
    
    async def _find_best_match(self, camera_embedding: np.ndarray, db_session) -> Optional[Dict[str, any]]:
        """Find best matching employee photo"""
        best_similarity = 0.0
        best_match = None
        
        try:
            # Get all employees with photos
            employee_service = EmployeeService()
            all_employees = employee_service.get_employees(db_session, skip=0, limit=1000)
            
            for employee in all_employees:
                employee_id = employee.employee_id
                
                # Get all recognition photos for this employee
                recognition_photos = photo_service.get_employee_recognition_photos(employee_id)
                
                for photo_path in recognition_photos:
                    try:
                        # Load and process photo
                        stored_image = cv2.imread(photo_path)
                        if stored_image is None:
                            logger.warning(f"Could not load photo: {photo_path}")
                            continue
                        
                        # Convert BGR to RGB
                        stored_image_rgb = cv2.cvtColor(stored_image, cv2.COLOR_BGR2RGB)
                        
                        # Extract embedding from stored photo
                        stored_result = await self.ai_service.process_recognition(stored_image_rgb)
                        
                        if not stored_result.get("face_detected") or stored_result.get("embedding") is None:
                            logger.warning(f"No valid face found in stored photo: {photo_path}")
                            continue
                        
                        stored_embedding = stored_result.get("embedding")
                        
                        # Calculate similarity
                        similarity = self._calculate_similarity(camera_embedding, stored_embedding)
                        
                        if similarity > best_similarity:
                            best_similarity = similarity
                            best_match = {
                                "employee_id": employee_id,
                                "similarity": similarity,
                                "photo_path": photo_path
                            }
                            
                    except Exception as e:
                        logger.error(f"Error processing photo {photo_path}: {e}")
                        continue
            
            return best_match
            
        except Exception as e:
            logger.error(f"Error finding best match: {e}")
            return None
    
    def _calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two face embeddings"""
        try:
            # Ensure embeddings are numpy arrays
            emb1 = np.array(embedding1).flatten()
            emb2 = np.array(embedding2).flatten()
            
            # Calculate cosine similarity
            dot_product = np.dot(emb1, emb2)
            norm1 = np.linalg.norm(emb1)
            norm2 = np.linalg.norm(emb2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            
            # Convert to range [0, 1]
            similarity = (similarity + 1) / 2
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    async def verify_employee_face(self, employee_id: str, camera_image: np.ndarray) -> Dict[str, any]:
        """
        Verify if camera image matches specific employee's stored photos
        Used for targeted verification
        """
        try:
            # Extract face embedding from camera image
            camera_result = await self.ai_service.process_recognition(camera_image)
            
            if not camera_result.get("face_detected"):
                return {
                    "verified": False,
                    "reason": "No face detected in camera image",
                    "confidence": 0.0
                }
            
            camera_embedding = camera_result.get("embedding")
            if camera_embedding is None:
                return {
                    "verified": False,
                    "reason": "Failed to extract face embedding",
                    "confidence": 0.0
                }
            
            # Get all photos for specific employee
            recognition_photos = photo_service.get_employee_recognition_photos(employee_id)
            
            if not recognition_photos:
                return {
                    "verified": False,
                    "reason": "No photos stored for this employee",
                    "confidence": 0.0
                }
            
            best_similarity = 0.0
            best_photo = None
            
            for photo_path in recognition_photos:
                try:
                    # Load and process photo
                    stored_image = cv2.imread(photo_path)
                    if stored_image is None:
                        continue
                    
                    # Convert BGR to RGB
                    stored_image_rgb = cv2.cvtColor(stored_image, cv2.COLOR_BGR2RGB)
                    
                    # Extract embedding
                    stored_result = await self.ai_service.process_recognition(stored_image_rgb)
                    
                    if not stored_result.get("face_detected") or stored_result.get("embedding") is None:
                        continue
                    
                    # Calculate similarity
                    similarity = self._calculate_similarity(camera_embedding, stored_result.get("embedding"))
                    
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_photo = photo_path
                        
                except Exception as e:
                    logger.error(f"Error processing photo {photo_path}: {e}")
                    continue
            
            is_verified = best_similarity >= self.similarity_threshold
            
            return {
                "verified": is_verified,
                "confidence": best_similarity,
                "threshold": self.similarity_threshold,
                "matched_photo": best_photo if is_verified else None,
                "total_photos_checked": len(recognition_photos),
                "processing_time": camera_result.get("processing_time", 0.0)
            }
            
        except Exception as e:
            logger.error(f"Error in employee verification: {e}")
            return {
                "verified": False,
                "reason": f"Verification error: {str(e)}",
                "confidence": 0.0
            }
    
    def get_recognition_stats(self) -> Dict[str, any]:
        """Get statistics about the recognition system"""
        try:
            storage_stats = photo_service.get_storage_stats()
            
            return {
                "total_employees_with_photos": storage_stats.get("total_employees", 0),
                "total_stored_photos": storage_stats.get("total_photos", 0),
                "total_storage_size": storage_stats.get("total_size_mb", 0),
                "similarity_threshold": self.similarity_threshold,
                "storage_path": storage_stats.get("storage_path", ""),
                "ai_models_loaded": {
                    "face_detection": self.ai_service.face_detector is not None,
                    "anti_spoofing": self.ai_service.anti_spoof_model is not None,
                    "face_recognition": self.ai_service.face_recognizer is not None
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting recognition stats: {e}")
            return {}

# Global instance
face_recognition_service = FaceRecognitionService()
