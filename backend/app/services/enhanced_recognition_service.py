"""
Enhanced Face Recognition Service with Rolling Template System
Integrates template manager for improved accuracy over time
"""
import numpy as np
import cv2
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.face_template import FaceTemplate
from app.models.employee import Employee
from app.services.enhanced_face_embedding_service import face_embedding_service as template_manager
from app.services.real_ai_service import get_ai_service
import logging
import datetime

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
        self.template_manager = template_manager
        
        # Recognition thresholds - LOWERED FOR TESTING
        self.RECOGNITION_THRESHOLD = 0.60  
        self.HIGH_CONFIDENCE_THRESHOLD = 0.75  
        self.VERY_HIGH_CONFIDENCE_THRESHOLD = 0.80
        
        # Learning thresholds
        self.MIN_QUALITY_FOR_LEARNING = 0.7
        self.MIN_CONFIDENCE_FOR_LEARNING = 0.7
        
        # Uploads directory
        self.uploads_dir = Path("data/uploads")
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
    
    def _save_recognition_image(self, image: np.ndarray, employee_id: str = None, 
                               similarity: float = None, suffix: str = None) -> str:
        """Save recognition image with timestamp and info"""
        try:
            timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            if employee_id and similarity:
                base_name = f"recognition_{employee_id}_{similarity:.3f}_{timestamp}"
                if suffix:
                    filename = f"{base_name}_{suffix}.jpg"
                else:
                    filename = f"{base_name}.jpg"
            else:
                filename = f"recognition_unknown_{timestamp}.jpg"
            
            filepath = self.uploads_dir / filename
            cv2.imwrite(str(filepath), image)
            
            logger.info(f"💾 Saved recognition image: {filename}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            return ""
    
    async def recognize_face(self, db: Session, face_image: np.ndarray, 
                           bbox: Optional[List[int]] = None) -> Dict:
        """
        Recognize face using rolling template system with anti-spoofing check
        """
        try:
            # 1. Anti-spoofing check - ENABLED FOR SECURITY
            is_real = self.ai_service.anti_spoofing(face_image, bbox)
            if not is_real:
                logger.warning("🚨 SPOOF DETECTED - rejecting recognition attempt")
                return {
                    "success": False,
                    "message": "Hệ thống phát hiện khuôn mặt không hợp lệ – vui lòng dùng khuôn mặt thật.",
                    "recognized": False
                }
            
            logger.info("✅ Anti-spoofing check passed - proceeding with recognition")
            
            # 2. Extract embedding from input face
            input_embedding = self.ai_service.extract_embedding(face_image, bbox)
            
            if input_embedding is None:
                return {
                    "success": False,
                    "message": "Failed to extract face embedding",
                    "recognized": False
                }
            
            # Get all active templates from database
            all_templates = db.query(FaceTemplate).all()
            
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
                # Save unrecognized face image
                saved_image_path = self._save_recognition_image(face_image)
                
                return {
                    "success": True,
                    "message": f"🚫 No matching template found | Recognition Threshold: {self.RECOGNITION_THRESHOLD} | Image saved: {os.path.basename(saved_image_path) if saved_image_path else 'Failed'}",
                    "recognized": False,
                    "similarity_scores": [],
                    "saved_image": saved_image_path,
                    "thresholds": {
                        "recognition": self.RECOGNITION_THRESHOLD,
                        "high_confidence": self.HIGH_CONFIDENCE_THRESHOLD,
                        "very_high_confidence": self.VERY_HIGH_CONFIDENCE_THRESHOLD
                    }
                }
            
            template, similarity, employee = best_match
            
            # Save recognition image
            saved_image_path = self._save_recognition_image(face_image, employee.employee_id, similarity)
            
            # DEBUG: TEMPORARILY ALWAYS RETURN EMPLOYEE INFO (regardless of threshold)
            logger.info(f"🔍 DEBUG: Best match - Employee {employee.employee_id} with similarity {similarity:.4f}")
            logger.info(f"🎯 Thresholds - Recognition: {self.RECOGNITION_THRESHOLD}, High: {self.HIGH_CONFIDENCE_THRESHOLD}, Very High: {self.VERY_HIGH_CONFIDENCE_THRESHOLD}")
            
            # Determine if recognition meets threshold (but still return employee info)
            meets_threshold = similarity >= self.RECOGNITION_THRESHOLD
            recognition_status = "recognized" if meets_threshold else "low_similarity"
            
            if meets_threshold:
                # Update template performance - direct database update
                template.match_count += 1
                template.last_matched = datetime.datetime.utcnow()
                if template.avg_match_confidence == 0.0:
                    template.avg_match_confidence = similarity
                else:
                    template.avg_match_confidence = (
                        (template.avg_match_confidence * (template.match_count - 1) + similarity) / template.match_count
                    )
                db.commit()
                
                # Check if we should learn from this recognition
                learning_result = await self._consider_template_learning(
                    db, employee.employee_id, face_image, similarity
                )
                
                # Log learning results
                if learning_result.get("learned", False):
                    logger.info(f"🎓 TEMPLATE LEARNING: Successfully created new template for {employee.employee_id}")
                    logger.info(f"📊 Learning details: {learning_result}")
            
            # Get confidence level
            confidence_level = self._get_confidence_level(similarity)
            
            # ALWAYS return employee information for debugging
            return {
                "success": True,
                "recognized": meets_threshold,  # True only if meets threshold
                "employee_id": employee.employee_id,
                "employee_name": employee.name,  # Use 'name' instead of 'full_name'
                "similarity": similarity,
                "confidence_level": confidence_level,
                "template_id": template.id,
                "image_id": template.image_id,
                "is_primary": template.is_primary,
                "template_source": template.created_from,
                "saved_image": saved_image_path,
                "thresholds": {
                    "recognition": self.RECOGNITION_THRESHOLD,
                    "high_confidence": self.HIGH_CONFIDENCE_THRESHOLD,
                    "very_high_confidence": self.VERY_HIGH_CONFIDENCE_THRESHOLD
                },
                "message": f"🎯 {recognition_status} | Similarity: {similarity:.4f} | Recognition Threshold: {self.RECOGNITION_THRESHOLD} | High: {self.HIGH_CONFIDENCE_THRESHOLD} | Very High: {self.VERY_HIGH_CONFIDENCE_THRESHOLD} | Image saved: {os.path.basename(saved_image_path) if saved_image_path else 'Failed'}",
                "employee": {  # Add full employee object for kiosk
                    "employee_id": employee.employee_id,
                    "name": employee.name,  # Use correct field name
                    "department": employee.department or "N/A",
                    "position": employee.position or "N/A", 
                    "email": employee.email or "N/A",
                    "avatar_url": f"/api/v1/employees/{employee.employee_id}/photo"  # Generate avatar URL
                }
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
                # Use CosineSimilarityCalculator directly
                from app.services.real_ai_service import CosineSimilarityCalculator
                similarity = CosineSimilarityCalculator.calculate(
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
            
            # Add as potential template - simplified approach
            # Check if we can add more templates for this employee
            existing_count = db.query(FaceTemplate).filter(
                FaceTemplate.employee_id == employee_id
            ).count()
            
            if existing_count < 4:  # Max 4 templates (0,1,2,3)
                # Find next available image_id
                used_ids = db.query(FaceTemplate.image_id).filter(
                    FaceTemplate.employee_id == employee_id
                ).all()
                used_ids = [row[0] for row in used_ids]
                
                next_id = None
                for i in range(1, 4):  # 1,2,3 (0 is reserved for avatar)
                    if i not in used_ids:
                        next_id = i
                        break
                
                if next_id:
                    logger.info(f"🎓 LEARNING: Starting template creation for employee {employee_id} with image_id {next_id}")
                    
                    # Extract embedding from the high-quality recognition image
                    input_embedding = self.ai_service.extract_embedding(face_image)
                    if input_embedding is None:
                        logger.error(f"Failed to extract embedding for learning - employee {employee_id}")
                        return
                    
                    # Create new face template for rolling learning
                    new_template = FaceTemplate(
                        employee_id=employee_id,
                        image_id=next_id,
                        embedding_vector=input_embedding.tolist(),
                        created_from="rolling_learning",  # Mark as learned template
                        is_primary=False,  # Only image_id=0 is primary
                        match_count=0,
                        avg_match_confidence=0.0,
                        created_at=datetime.datetime.utcnow(),
                        quality_score=quality_score  # Store the quality score
                    )
                    
                    # Save template to database
                    db.add(new_template)
                    db.commit()
                    db.refresh(new_template)
                    
                    # Save the learning image for reference
                    learning_image_path = self._save_recognition_image(
                        face_image, employee_id, match_confidence, suffix="learning"
                    )
                    
                    logger.info(f"✅ LEARNING SUCCESS: Created template {new_template.id} for employee {employee_id}")
                    logger.info(f"📊 Template stats: image_id={next_id}, quality={quality_score:.3f}, confidence={match_confidence:.3f}")
                    logger.info(f"💾 Learning image saved: {learning_image_path}")
                    
                    return {
                        "learned": True,
                        "template_id": new_template.id,
                        "image_id": next_id,
                        "quality_score": quality_score,
                        "confidence": match_confidence,
                        "learning_image": learning_image_path
                    }
                else:
                    logger.info(f"🚫 No available slot for learning - employee {employee_id} (max templates reached)")
                    
                    # ========== TEMPLATE REPLACEMENT LOGIC ==========
                    # When no slots available, consider replacing worst template
                    replacement_result = await self._consider_template_replacement(
                        db, employee_id, face_image, match_confidence, quality_score
                    )
                    
                    if replacement_result.get("replaced", False):
                        logger.info(f"� TEMPLATE REPLACEMENT SUCCESS: {replacement_result}")
                        return replacement_result
                    else:
                        logger.info(f"⚠️ No template replacement performed: {replacement_result.get('reason', 'Unknown')}")
            else:
                logger.info(f"�📊 Employee {employee_id} already has max templates ({existing_count}/4)")
                
                # Even when count check fails, still try replacement  
                replacement_result = await self._consider_template_replacement(
                    db, employee_id, face_image, match_confidence, quality_score
                )
                
                if replacement_result.get("replaced", False):
                    return replacement_result
                
            return {"learned": False, "reason": "No learning opportunity - max templates reached"}
            
        except Exception as e:
            logger.error(f"Error in template learning: {e}")
            return {"learned": False, "reason": f"Error: {str(e)}"}
    
    async def _consider_template_replacement(self, db: Session, employee_id: str, 
                                           face_image: np.ndarray, match_confidence: float,
                                           new_quality_score: float) -> Dict:
        """
        Consider replacing existing template when no slots available
        
        Replacement Strategy:
        1. Never replace primary template (image_id=0)
        2. Find worst performing template among learning templates (1,2,3)
        3. Replace if new template is significantly better
        """
        try:
            # Get all learning templates (exclude primary image_id=0)
            learning_templates = db.query(FaceTemplate).filter(
                FaceTemplate.employee_id == employee_id,
                FaceTemplate.image_id > 0,  # Only learning templates
                FaceTemplate.created_from == "rolling_learning"
            ).all()
            
            if not learning_templates:
                return {
                    "replaced": False,
                    "reason": "No learning templates available for replacement"
                }
            
            # Calculate replacement scores for each template
            replacement_candidates = []
            
            for template in learning_templates:
                # Calculate replacement score (lower = worse template, higher priority for replacement)
                replacement_score = self._calculate_template_replacement_score(template)
                
                replacement_candidates.append({
                    "template": template,
                    "replacement_score": replacement_score,
                    "template_id": template.id,
                    "image_id": template.image_id,
                    "quality_score": template.quality_score or 0.0,
                    "match_count": template.match_count,
                    "avg_confidence": template.avg_match_confidence or 0.0
                })
            
            # Sort by replacement score (lowest first - worst templates)
            replacement_candidates.sort(key=lambda x: x["replacement_score"])
            worst_template_info = replacement_candidates[0]
            worst_template = worst_template_info["template"]
            
            # Decision logic: Replace if new template is significantly better
            should_replace = self._should_replace_template(
                worst_template_info, new_quality_score, match_confidence
            )
            
            if should_replace:
                logger.info(f"🔄 REPLACING TEMPLATE: employee={employee_id}, old_template_id={worst_template.id}")
                logger.info(f"📊 Replacement reason: {should_replace}")
                
                # Extract embedding from new face
                new_embedding = self.ai_service.extract_embedding(face_image)
                if new_embedding is None:
                    return {
                        "replaced": False,
                        "reason": "Failed to extract embedding for replacement"
                    }
                
                # Update existing template with new data
                old_image_id = worst_template.image_id
                old_quality = worst_template.quality_score
                old_confidence = worst_template.avg_match_confidence
                
                worst_template.embedding_vector = new_embedding.tolist()
                worst_template.quality_score = new_quality_score
                worst_template.match_count = 0  # Reset match count
                worst_template.avg_match_confidence = 0.0  # Will be updated on first match
                worst_template.created_at = datetime.datetime.utcnow()  # Update timestamp
                worst_template.last_matched = None  # Reset last matched
                
                db.commit()
                
                # Save replacement image
                replacement_image_path = self._save_recognition_image(
                    face_image, employee_id, match_confidence, suffix=f"replacement_{old_image_id}"
                )
                
                logger.info(f"✅ TEMPLATE REPLACEMENT COMPLETE:")
                logger.info(f"   Template ID: {worst_template.id} (image_id={old_image_id})")
                logger.info(f"   Quality: {old_quality:.3f} → {new_quality_score:.3f}")
                logger.info(f"   Confidence: {old_confidence:.3f} → {match_confidence:.3f}")
                logger.info(f"   Image saved: {replacement_image_path}")
                
                return {
                    "replaced": True,
                    "action": "template_replacement",
                    "template_id": worst_template.id,
                    "image_id": old_image_id,
                    "old_quality": old_quality,
                    "new_quality": new_quality_score,
                    "old_confidence": old_confidence,
                    "new_confidence": match_confidence,
                    "replacement_image": replacement_image_path,
                    "improvement": {
                        "quality_gain": new_quality_score - old_quality,
                        "confidence_gain": match_confidence - old_confidence
                    }
                }
            else:
                return {
                    "replaced": False,
                    "reason": f"New template not significantly better than worst existing template",
                    "worst_template_score": worst_template_info["replacement_score"],
                    "new_quality": new_quality_score,
                    "new_confidence": match_confidence
                }
                
        except Exception as e:
            logger.error(f"Error in template replacement consideration: {e}")
            return {
                "replaced": False,
                "reason": f"Replacement error: {str(e)}"
            }
    
    def _calculate_template_replacement_score(self, template: FaceTemplate) -> float:
        """
        Calculate replacement priority score for a template
        Lower score = higher priority for replacement (worse template)
        
        Factors:
        - Quality score (40% weight)
        - Match count (30% weight) - less used = more likely to replace
        - Average confidence (20% weight)
        - Age (10% weight) - older templates preferred for replacement
        """
        try:
            # Quality component (0-1, higher = better)
            quality_component = template.quality_score or 0.0
            
            # Usage component (normalize match_count, lower usage = higher replacement priority)
            # Cap at 100 matches for normalization
            usage_component = min(template.match_count / 100.0, 1.0)
            
            # Confidence component (0-1, higher = better)
            confidence_component = template.avg_match_confidence or 0.0
            
            # Age component (older = higher replacement priority)
            # Calculate days since creation, cap at 30 days
            if template.created_at:
                age_days = (datetime.datetime.utcnow() - template.created_at).days
                age_component = min(age_days / 30.0, 1.0)  # Older = higher score = lower replacement priority (inverted)
                age_component = 1.0 - age_component  # Invert: older = lower score = higher replacement priority
            else:
                age_component = 0.0
            
            # Weighted combination (lower = higher replacement priority)
            replacement_score = (
                quality_component * 0.4 +      # Quality: lower quality = lower score
                usage_component * 0.3 +        # Usage: less used = lower score  
                confidence_component * 0.2 +   # Confidence: lower confidence = lower score
                age_component * 0.1             # Age: older = lower score
            )
            
            logger.debug(f"Template {template.id} replacement score: {replacement_score:.3f} "
                        f"(Q:{quality_component:.2f}, U:{usage_component:.2f}, "
                        f"C:{confidence_component:.2f}, A:{age_component:.2f})")
            
            return replacement_score
            
        except Exception as e:
            logger.error(f"Error calculating replacement score for template {template.id}: {e}")
            return 0.5  # Default medium score
    
    def _should_replace_template(self, worst_template_info: Dict, 
                               new_quality: float, new_confidence: float) -> str:
        """
        Determine if we should replace the worst template with new data
        
        Returns:
        - String with reason if should replace
        - False if should not replace
        """
        try:
            old_quality = worst_template_info["quality_score"]
            old_confidence = worst_template_info["avg_confidence"]
            old_match_count = worst_template_info["match_count"]
            
            # Replacement criteria (any of these conditions)
            
            # 1. Significant quality improvement
            quality_improvement = new_quality - old_quality
            if quality_improvement >= 0.15:  # 15% quality improvement
                return f"Quality improvement: {quality_improvement:.3f} (≥0.15 threshold)"
            
            # 2. Significant confidence improvement  
            confidence_improvement = new_confidence - old_confidence
            if confidence_improvement >= 0.10:  # 10% confidence improvement
                return f"Confidence improvement: {confidence_improvement:.3f} (≥0.10 threshold)"
            
            # 3. Old template has very low usage (likely poor quality)
            if old_match_count <= 2 and (quality_improvement > 0 or confidence_improvement > 0):
                return f"Low usage template ({old_match_count} matches) with any improvement"
            
            # 4. Old template has very poor quality
            if old_quality < 0.5 and new_quality >= 0.7:
                return f"Poor quality template replacement: {old_quality:.3f} → {new_quality:.3f}"
            
            # 5. Combined moderate improvements
            if quality_improvement >= 0.08 and confidence_improvement >= 0.05:
                return f"Combined improvements: Q+{quality_improvement:.3f}, C+{confidence_improvement:.3f}"
            
            # No significant improvement
            return False
            
        except Exception as e:
            logger.error(f"Error in replacement decision: {e}")
            return False
    
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
    
    async def get_rolling_templates_status(self, db: Session) -> Dict:
        """Get comprehensive status of rolling templates system"""
        try:
            # Get all templates grouped by employee
            all_templates = db.query(FaceTemplate).all()
            
            stats = {
                "total_templates": len(all_templates),
                "employees": {},
                "templates_by_source": {},
                "learning_stats": {
                    "total_learned_templates": 0,
                    "employees_with_learning": 0,
                    "avg_learning_quality": 0.0,
                    "total_replacements": 0,
                    "avg_replacement_improvement": 0.0
                },
                "replacement_stats": {
                    "quality_driven_replacements": 0,
                    "confidence_driven_replacements": 0, 
                    "usage_driven_replacements": 0,
                    "combined_driven_replacements": 0
                }
            }
            
            for template in all_templates:
                employee_id = template.employee_id
                
                # Initialize employee stats
                if employee_id not in stats["employees"]:
                    stats["employees"][employee_id] = {
                        "total_templates": 0,
                        "templates": [],
                        "learning_capacity": 0  # How many more templates can be learned
                    }
                
                # Count by source
                source = template.created_from
                if source not in stats["templates_by_source"]:
                    stats["templates_by_source"][source] = 0
                stats["templates_by_source"][source] += 1
                
                # Track learning templates
                if source == "rolling_learning":
                    stats["learning_stats"]["total_learned_templates"] += 1
                    if template.quality_score:
                        stats["learning_stats"]["avg_learning_quality"] += template.quality_score
                
                # Add to employee stats
                emp_stats = stats["employees"][employee_id]
                emp_stats["total_templates"] += 1
                emp_stats["templates"].append({
                    "template_id": template.id,
                    "image_id": template.image_id,
                    "created_from": template.created_from,
                    "quality_score": template.quality_score,
                    "match_count": template.match_count,
                    "avg_confidence": template.avg_match_confidence,
                    "is_primary": template.is_primary,
                    "created_at": template.created_at
                })
                
                # Calculate learning capacity (max 4 templates per employee)
                emp_stats["learning_capacity"] = max(0, 4 - emp_stats["total_templates"])
            
            # Calculate employees with learning templates
            for emp_id, emp_data in stats["employees"].items():
                has_learning = any(t["created_from"] == "rolling_learning" for t in emp_data["templates"])
                if has_learning:
                    stats["learning_stats"]["employees_with_learning"] += 1
            
            # Calculate average learning quality
            if stats["learning_stats"]["total_learned_templates"] > 0:
                stats["learning_stats"]["avg_learning_quality"] /= stats["learning_stats"]["total_learned_templates"]
                
            return stats
            
        except Exception as e:
            logger.error(f"Error getting rolling templates status: {e}")
            return {"error": str(e)}
    
    async def get_employee_recognition_stats(self, db: Session, employee_id: str) -> Dict:
        """Get recognition statistics for an employee"""
        try:
            templates = db.query(FaceTemplate).filter(
                FaceTemplate.employee_id == employee_id
            ).order_by(FaceTemplate.image_id).all()
            
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
                    "image_id": template.image_id,
                    "is_primary": template.is_primary,
                    "filename": template.filename,
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
    
    async def register_face(self, db: Session, face_image: np.ndarray, 
                           employee_id: str, device_id: str = None) -> Dict:
        """
        Register a new face for an employee with anti-spoofing check
        """
        try:
            # 1. Anti-spoofing check - ENABLED FOR SECURITY
            is_real = self.ai_service.anti_spoofing(face_image)
            if not is_real:
                logger.warning(f"🚨 SPOOF DETECTED during registration for employee {employee_id}")
                return {
                    "success": False,
                    "message": "Spoof detected in registration image - please use a real photo",
                    "employee_id": employee_id
                }
            
            logger.info(f"✅ Anti-spoofing check passed for employee {employee_id} registration")
            
            # 2. Detect face
            found, bbox = self.ai_service.detect_face(face_image)
            if not found:
                return {
                    "success": False,
                    "message": "No face detected in registration image",
                    "employee_id": employee_id
                }
            
            # 3. Extract embedding
            input_embedding = self.ai_service.extract_embedding(face_image, bbox)
            if input_embedding is None:
                return {
                    "success": False,
                    "message": "Failed to extract face embedding from registration image",
                    "employee_id": employee_id
                }
            
            # 4. Check if employee exists
            employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
            if not employee:
                return {
                    "success": False,
                    "message": f"Employee {employee_id} not found in database",
                    "employee_id": employee_id
                }
            
            # 5. Find next available image_id for this employee
            existing_templates = db.query(FaceTemplate).filter(
                FaceTemplate.employee_id == employee_id
            ).order_by(FaceTemplate.image_id).all()
            
            used_image_ids = [t.image_id for t in existing_templates]
            next_image_id = 0  # Start with 0 (avatar)
            while next_image_id in used_image_ids and next_image_id < 4:
                next_image_id += 1
            
            if next_image_id >= 4:
                return {
                    "success": False,
                    "message": f"Maximum templates (4) already exist for employee {employee_id}",
                    "employee_id": employee_id,
                    "existing_templates": len(existing_templates)
                }
            
            # 6. Create new face template
            new_template = FaceTemplate(
                employee_id=employee_id,
                image_id=next_image_id,
                embedding_vector=input_embedding.tolist(),
                created_from="registration",
                is_primary=(next_image_id == 0),  # First template is primary
                match_count=0,
                avg_match_confidence=0.0,
                created_at=datetime.datetime.utcnow()
            )
            
            db.add(new_template)
            db.commit()
            db.refresh(new_template)
            
            # 7. Save registration image
            saved_image_path = self._save_recognition_image(face_image, employee_id, 1.0)
            
            logger.info(f"✅ Registered face template for employee {employee_id} with image_id {next_image_id}")
            
            return {
                "success": True,
                "message": f"Face registered successfully for employee {employee_id}",
                "employee_id": employee_id,
                "template_id": new_template.id,
                "image_id": next_image_id,
                "is_primary": new_template.is_primary,
                "total_templates": len(existing_templates) + 1,
                "saved_image": saved_image_path,
                "device_id": device_id
            }
            
        except Exception as e:
            logger.error(f"Error in face registration for employee {employee_id}: {e}")
            db.rollback()
            return {
                "success": False,
                "message": f"Registration error: {str(e)}",
                "employee_id": employee_id
            }
    
    def get_service_status(self) -> Dict:
        """
        Get enhanced recognition service status
        """
        try:
            return {
                "status": "active",
                "service_type": "enhanced_recognition",
                "ai_enabled": True,
                "models": {
                    "face_detection": self.ai_service.face_detector is not None,
                    "anti_spoofing": self.ai_service.anti_spoof_model is not None,
                    "face_recognition": self.ai_service.face_recognizer is not None
                },
                "thresholds": {
                    "recognition": self.RECOGNITION_THRESHOLD,
                    "high_confidence": self.HIGH_CONFIDENCE_THRESHOLD,
                    "very_high_confidence": self.VERY_HIGH_CONFIDENCE_THRESHOLD,
                    "min_quality_learning": self.MIN_QUALITY_FOR_LEARNING,
                    "min_confidence_learning": self.MIN_CONFIDENCE_FOR_LEARNING
                },
                "model_path": str(self.ai_service.model_path),
                "uploads_dir": str(self.uploads_dir)
            }
            
        except Exception as e:
            logger.error(f"Error getting service status: {e}")
            return {
                "status": "error",
                "service_type": "enhanced_recognition",
                "ai_enabled": False,
                "error": str(e)
            }
    
    def health_check(self) -> Dict:
        """
        Enhanced recognition service health check
        """
        try:
            # Check if AI service is available
            if not self.ai_service:
                return {
                    "healthy": False,
                    "message": "AI service not available",
                    "models": {}
                }
            
            # Test if models are loaded
            models_loaded = {
                "detection": self.ai_service.face_detector is not None,
                "anti_spoofing": self.ai_service.anti_spoof_model is not None, 
                "recognition": self.ai_service.face_recognizer is not None
            }
            
            all_models_loaded = all(models_loaded.values())
            
            return {
                "healthy": all_models_loaded,
                "models": models_loaded,
                "service_type": "enhanced_recognition",
                "thresholds_configured": True,
                "uploads_dir_exists": self.uploads_dir.exists(),
                "message": "All AI models loaded and service ready" if all_models_loaded else "Some AI models missing"
            }
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "message": "Enhanced recognition service unavailable"
            }

# Singleton instance
_enhanced_recognition_service = None

def get_enhanced_recognition_service() -> EnhancedRecognitionService:
    """Get singleton enhanced recognition service"""
    global _enhanced_recognition_service
    if _enhanced_recognition_service is None:
        _enhanced_recognition_service = EnhancedRecognitionService()
    return _enhanced_recognition_service
