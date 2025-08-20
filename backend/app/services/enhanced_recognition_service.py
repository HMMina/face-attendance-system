"""
Enhanced Face Recognition Service with Rolling Template System
Integrates template manager for improved accuracy over time
"""
import numpy as np
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.face_template import FaceTemplate
from app.models.employee import Employee
from app.services.template_manager_service import TemplateManagerService
from app.services.real_ai_service import get_ai_service
import logging

logger = logging.getLogger(__name__)

class EnhancedRecognitionService:
    """
    Enhanced face recognition using rolling template system
    - Uses multiple templates per employee for better accuracy
    - Learns from successful matches
    - Automatically updates templates
    """
    
    def __init__(self):
        self.ai_service = get_ai_service()
        self.template_manager = TemplateManagerService()
        
        # Recognition thresholds
        self.RECOGNITION_THRESHOLD = 0.75
        self.HIGH_CONFIDENCE_THRESHOLD = 0.85
        self.VERY_HIGH_CONFIDENCE_THRESHOLD = 0.90
        
        # Learning thresholds
        self.MIN_QUALITY_FOR_LEARNING = 0.8
        self.MIN_CONFIDENCE_FOR_LEARNING = 0.85
    
    async def recognize_face(self, db: Session, face_image: np.ndarray, 
                           bbox: Optional[List[int]] = None) -> Dict:
        """
        Recognize face using rolling template system
        """
        try:
            # Extract embedding from input face
            input_embedding = self.ai_service.extract_embedding(face_image, bbox)
            
            if input_embedding is None:
                return {
                    "success": False,
                    "message": "Failed to extract face embedding",
                    "recognized": False
                }
            
            # Get all active templates
            all_templates = await self.template_manager.get_all_active_templates(db)
            
            if not all_templates:
                return {
                    "success": True,
                    "message": "No templates available for recognition",
                    "recognized": False
                }
            
            # Calculate similarities with all templates
            best_match = await self._find_best_template_match(
                input_embedding, all_templates
            )
            
            if not best_match:
                return {
                    "success": True,
                    "message": "No matching template found",
                    "recognized": False,
                    "similarity_scores": []
                }
            
            template, similarity, employee = best_match
            
            # Check recognition threshold
            if similarity < self.RECOGNITION_THRESHOLD:
                return {
                    "success": True,
                    "message": f"Similarity below threshold: {similarity:.3f}",
                    "recognized": False,
                    "best_similarity": similarity,
                    "employee_id": employee.employee_id
                }
            
            # Update template performance
            await self.template_manager.update_template_performance(
                db, template.id, similarity
            )
            
            # Check if we should learn from this recognition
            await self._consider_template_learning(
                db, employee.employee_id, face_image, similarity
            )
            
            # Get confidence level
            confidence_level = self._get_confidence_level(similarity)
            
            return {
                "success": True,
                "recognized": True,
                "employee_id": employee.employee_id,
                "employee_name": employee.full_name,
                "similarity": similarity,
                "confidence_level": confidence_level,
                "template_id": template.id,
                "template_order": template.template_order,
                "template_source": template.created_from,
                "message": f"Recognized with {confidence_level} confidence"
            }
            
        except Exception as e:
            logger.error(f"Error in face recognition: {e}")
            return {
                "success": False,
                "message": f"Recognition error: {str(e)}",
                "recognized": False
            }
    
    async def _find_best_template_match(self, input_embedding: np.ndarray,
                                      templates: List[FaceTemplate]) -> Optional[Tuple]:
        """Find best matching template"""
        
        best_similarity = 0.0
        best_template = None
        best_employee = None
        
        # Group templates by employee for better processing
        employee_templates = {}
        for template in templates:
            if template.employee_id not in employee_templates:
                employee_templates[template.employee_id] = []
            employee_templates[template.employee_id].append(template)
        
        # Find best match per employee, then overall best
        for employee_id, emp_templates in employee_templates.items():
            # Calculate similarity with all templates for this employee
            similarities = []
            
            for template in emp_templates:
                template_embedding = np.array(template.embedding_vector)
                similarity = self.ai_service.calculator.calculate(
                    input_embedding, template_embedding
                )
                similarities.append((template, similarity))
            
            # Get best template for this employee
            if similarities:
                best_emp_template, best_emp_similarity = max(
                    similarities, key=lambda x: x[1]
                )
                
                # Check if this is overall best
                if best_emp_similarity > best_similarity:
                    best_similarity = best_emp_similarity
                    best_template = best_emp_template
                    # Get employee info
                    from sqlalchemy.orm import Session
                    if hasattr(templates[0], '_sa_instance_state'):
                        # Get session from template instance
                        session = Session.object_session(templates[0])
                        best_employee = session.query(Employee).filter(
                            Employee.employee_id == employee_id
                        ).first()
        
        if best_template and best_employee:
            return (best_template, best_similarity, best_employee)
        
        return None
    
    async def _consider_template_learning(self, db: Session, employee_id: str,
                                        face_image: np.ndarray, match_confidence: float):
        """Consider if we should learn from this recognition"""
        
        try:
            # Only learn from high-confidence matches
            if match_confidence < self.MIN_CONFIDENCE_FOR_LEARNING:
                return
            
            # Calculate image quality
            quality_score = self._calculate_image_quality(face_image)
            
            if quality_score < self.MIN_QUALITY_FOR_LEARNING:
                return
            
            # Add as potential template
            result = await self.template_manager.add_attendance_template(
                db, employee_id, face_image, quality_score, match_confidence
            )
            
            if result["success"]:
                logger.info(f"Added learning template for {employee_id}: {result['message']}")
            
        except Exception as e:
            logger.error(f"Error in template learning: {e}")
    
    def _calculate_image_quality(self, image: np.ndarray) -> float:
        """Calculate basic image quality score"""
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Calculate Laplacian variance (focus measure)
            import cv2
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Normalize to 0-1 range (threshold at 100 for decent focus)
            focus_score = min(laplacian_var / 100.0, 1.0)
            
            # Calculate brightness (0.3-0.7 is good range)
            brightness = gray.mean() / 255.0
            brightness_score = 1.0 - abs(brightness - 0.5) * 2
            
            # Combined quality score
            quality = (focus_score * 0.7 + brightness_score * 0.3)
            
            return min(max(quality, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating image quality: {e}")
            return 0.5  # Default medium quality
    
    def _get_confidence_level(self, similarity: float) -> str:
        """Get confidence level description"""
        if similarity >= self.VERY_HIGH_CONFIDENCE_THRESHOLD:
            return "VERY_HIGH"
        elif similarity >= self.HIGH_CONFIDENCE_THRESHOLD:
            return "HIGH"
        elif similarity >= self.RECOGNITION_THRESHOLD:
            return "MEDIUM"
        else:
            return "LOW"
    
    async def get_employee_recognition_stats(self, db: Session, employee_id: str) -> Dict:
        """Get recognition statistics for an employee"""
        try:
            templates = await self.template_manager.get_employee_templates(db, employee_id)
            
            if not templates:
                return {"error": "No templates found"}
            
            stats = {
                "employee_id": employee_id,
                "total_templates": len(templates),
                "templates": []
            }
            
            total_matches = 0
            total_confidence = 0.0
            
            for template in templates:
                template_stats = {
                    "template_id": template.id,
                    "template_order": template.template_order,
                    "created_from": template.created_from,
                    "age_days": template.age_days,
                    "match_count": template.match_count,
                    "avg_confidence": template.avg_match_confidence,
                    "quality_score": template.quality_score,
                    "last_matched": template.last_matched
                }
                
                stats["templates"].append(template_stats)
                total_matches += template.match_count
                if template.avg_match_confidence:
                    total_confidence += template.avg_match_confidence
            
            stats["total_matches"] = total_matches
            stats["overall_avg_confidence"] = total_confidence / len(templates) if templates else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting recognition stats: {e}")
            return {"error": str(e)}
    
    async def batch_recognize_faces(self, db: Session, face_images: List[np.ndarray],
                                  bboxes: Optional[List[List[int]]] = None) -> List[Dict]:
        """Recognize multiple faces in batch"""
        results = []
        
        for i, face_image in enumerate(face_images):
            bbox = bboxes[i] if bboxes and i < len(bboxes) else None
            result = await self.recognize_face(db, face_image, bbox)
            results.append(result)
        
        return results
    
    async def update_recognition_thresholds(self, recognition_threshold: float = None,
                                          high_confidence_threshold: float = None,
                                          very_high_confidence_threshold: float = None):
        """Update recognition thresholds"""
        if recognition_threshold is not None:
            self.RECOGNITION_THRESHOLD = recognition_threshold
        if high_confidence_threshold is not None:
            self.HIGH_CONFIDENCE_THRESHOLD = high_confidence_threshold
        if very_high_confidence_threshold is not None:
            self.VERY_HIGH_CONFIDENCE_THRESHOLD = very_high_confidence_threshold
        
        logger.info(f"Updated thresholds: Recognition={self.RECOGNITION_THRESHOLD}, "
                   f"High={self.HIGH_CONFIDENCE_THRESHOLD}, VeryHigh={self.VERY_HIGH_CONFIDENCE_THRESHOLD}")

# Singleton instance
_enhanced_recognition_service = None

def get_enhanced_recognition_service() -> EnhancedRecognitionService:
    """Get singleton enhanced recognition service"""
    global _enhanced_recognition_service
    if _enhanced_recognition_service is None:
        _enhanced_recognition_service = EnhancedRecognitionService()
    return _enhanced_recognition_service
