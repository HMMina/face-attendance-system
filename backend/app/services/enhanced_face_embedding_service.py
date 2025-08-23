"""
Enhanced Face Embedding Service
Handles face embedding extraction and storage with advanced template management
"""
import os
import shutil
import datetime
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
from PIL import Image
import cv2
import logging
from sqlalchemy.orm import Session

# Import AI models (placeholder - install insightface when ready)
try:
    import insightface
    from insightface.app import FaceAnalysis
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False
    logging.warning("InsightFace not available. Using dummy embeddings.")

from app.models.face_template import FaceTemplate
from app.models.employee import Employee
from app.config.database import get_db

logger = logging.getLogger(__name__)

class FaceEmbeddingService:
    """Enhanced service for face embedding extraction and management"""
    
    def __init__(self):
        self.base_photos_dir = Path("C:/Users/ADMIN/.vscode/face-attendace-system/backend/data/employee_photos")
        self.base_photos_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize face analysis model
        self.face_analyzer = None
        self._init_face_analyzer()
    
    def _init_face_analyzer(self):
        """Initialize InsightFace model for face embedding"""
        if INSIGHTFACE_AVAILABLE:
            try:
                self.face_analyzer = FaceAnalysis(
                    providers=['CPUExecutionProvider'],  # Use CPU for now
                    allowed_modules=['detection', 'recognition']
                )
                self.face_analyzer.prepare(ctx_id=0, det_size=(640, 640))
                logger.info("InsightFace model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load InsightFace model: {e}")
                self.face_analyzer = None
        else:
            logger.warning("InsightFace not available. Face embedding will use dummy data.")
    
    def get_employee_photo_dir(self, employee_id: str) -> Path:
        """Get the photo directory for a specific employee"""
        employee_dir = self.base_photos_dir / employee_id
        employee_dir.mkdir(parents=True, exist_ok=True)
        return employee_dir
    
    def extract_face_embedding(self, image_data: bytes) -> Tuple[Optional[np.ndarray], float, Dict[str, Any]]:
        """
        Extract face embedding from image data
        Returns: (embedding_vector, confidence_score, metadata)
        """
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Could not decode image")
            
            # Convert BGR to RGB for InsightFace
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            if self.face_analyzer is not None:
                # Use InsightFace for real embedding
                faces = self.face_analyzer.get(image_rgb)
                
                if len(faces) == 0:
                    logger.warning("No face detected in image")
                    return None, 0.0, {"error": "No face detected"}
                
                if len(faces) > 1:
                    logger.warning(f"Multiple faces detected ({len(faces)}), using the largest one")
                
                # Get the face with largest bounding box
                largest_face = max(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))
                
                # Extract embedding
                embedding = largest_face.embedding
                confidence = float(largest_face.det_score) if hasattr(largest_face, 'det_score') else 0.9
                
                metadata = {
                    "face_count": len(faces),
                    "bbox": largest_face.bbox.tolist(),
                    "age": int(largest_face.age) if hasattr(largest_face, 'age') else None,
                    "gender": largest_face.sex if hasattr(largest_face, 'sex') else None,
                    "embedding_size": len(embedding)
                }
                
                return embedding, confidence, metadata
            
            else:
                # Fallback: Generate dummy embedding for development
                logger.warning("Using dummy embedding - InsightFace not available")
                dummy_embedding = np.random.random(512).astype(np.float32)
                dummy_confidence = 0.8
                metadata = {
                    "face_count": 1,
                    "embedding_size": 512,
                    "note": "Dummy embedding for development"
                }
                
                return dummy_embedding, dummy_confidence, metadata
                
        except Exception as e:
            logger.error(f"Error extracting face embedding: {e}")
            return None, 0.0, {"error": str(e)}
    
    def save_employee_photo(self, employee_id: str, image_data: bytes, 
                           filename: str, image_id: int) -> Tuple[str, str]:
        """
        Save employee photo to filesystem
        Returns: (filename, full_file_path)
        """
        try:
            employee_dir = self.get_employee_photo_dir(employee_id)
            
            # Generate unique filename with image_id
            file_extension = Path(filename).suffix.lower()
            if not file_extension:
                file_extension = '.jpg'
            
            # Create filename with image_id prefix
            if image_id == 0:
                new_filename = f"avatar_{employee_id}{file_extension}"
            else:
                new_filename = f"photo_{image_id}_{employee_id}{file_extension}"
            
            file_path = employee_dir / new_filename
            
            # Save image file
            with open(file_path, 'wb') as f:
                f.write(image_data)
            
            logger.info(f"Saved photo for employee {employee_id}: {file_path}")
            return new_filename, str(file_path)
            
        except Exception as e:
            logger.error(f"Error saving photo for employee {employee_id}: {e}")
            raise
    
    def process_employee_photos(self, employee_id: str, photos_data: List[Dict[str, Any]], 
                               selected_avatar_index: int = 0) -> List[Dict[str, Any]]:
        """
        Process multiple photos for an employee and create face templates
        
        Args:
            employee_id: Employee ID
            photos_data: List of {filename, data} dictionaries
            selected_avatar_index: Index of photo to use as avatar (default: 0)
        
        Returns:
            List of processing results
        """
        results = []
        
        try:
            logger.info(f"Processing {len(photos_data)} photos for employee {employee_id}")
            
            for idx, photo_data in enumerate(photos_data):
                # Determine image_id
                if idx == selected_avatar_index:
                    image_id = 0  # Avatar
                    is_primary = True
                else:
                    # Assign image_id 1, 2, 3 for non-avatar photos
                    non_avatar_idx = idx if idx < selected_avatar_index else idx - 1
                    image_id = non_avatar_idx + 1
                    is_primary = False
                
                # Skip if image_id would be > 3
                if image_id > 3:
                    logger.warning(f"Skipping photo {idx} - maximum 4 photos allowed (1 avatar + 3 secondary)")
                    continue
                
                # Extract face embedding
                embedding, confidence, metadata = self.extract_face_embedding(photo_data['data'])
                
                if embedding is None:
                    logger.error(f"Failed to extract embedding from photo {idx}")
                    results.append({
                        'index': idx,
                        'image_id': image_id,
                        'success': False,
                        'error': metadata.get('error', 'Failed to extract embedding')
                    })
                    continue
                
                # Save photo to filesystem
                filename, file_path = self.save_employee_photo(
                    employee_id, photo_data['data'], photo_data['filename'], image_id
                )
                
                # Calculate quality score (placeholder - can be enhanced)
                quality_score = min(confidence * 1.2, 1.0)  # Boost confidence slightly for quality
                
                result = {
                    'index': idx,
                    'image_id': image_id,
                    'is_primary': is_primary,
                    'filename': filename,
                    'file_path': file_path,
                    'embedding': embedding.tolist(),  # Convert numpy to list for JSON serialization
                    'confidence_score': float(confidence),
                    'quality_score': float(quality_score),
                    'metadata': metadata,
                    'success': True
                }
                
                results.append(result)
                logger.info(f"Successfully processed photo {idx} as image_id {image_id} for employee {employee_id}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing photos for employee {employee_id}: {e}")
            raise
    
    def create_face_templates(self, db: Session, employee_id: str, 
                             processing_results: List[Dict[str, Any]]) -> List[FaceTemplate]:
        """
        Create FaceTemplate records in database from processing results
        """
        try:
            face_templates = []
            
            for result in processing_results:
                if not result['success']:
                    continue
                
                face_template = FaceTemplate(
                    employee_id=employee_id,
                    image_id=result['image_id'],
                    filename=result['filename'],
                    file_path=result['file_path'],
                    embedding_vector=result['embedding'],
                    is_primary=result['is_primary'],
                    created_from='ADMIN_UPLOAD',
                    quality_score=result['quality_score'],
                    confidence_score=result['confidence_score']
                )
                
                db.add(face_template)
                face_templates.append(face_template)
                logger.info(f"Created FaceTemplate record for employee {employee_id}, image_id {result['image_id']}")
            
            db.commit()
            logger.info(f"Successfully created {len(face_templates)} face templates for employee {employee_id}")
            return face_templates
            
        except Exception as e:
            logger.error(f"Error creating face templates for employee {employee_id}: {e}")
            db.rollback()
            raise
    
    def update_employee_templates(self, db: Session, employee_id: str, 
                                 new_photos_data: List[Dict[str, Any]], 
                                 selected_avatar_index: int = 0) -> Dict[str, Any]:
        """
        Update employee face templates with new photos
        Strategy: Keep avatar (image_id=0), replace secondary templates (image_id=1,2,3)
        """
        try:
            logger.info(f"Updating face templates for employee {employee_id}")
            
            # Get existing templates
            existing_templates = db.query(FaceTemplate).filter(
                FaceTemplate.employee_id == employee_id
            ).all()
            
            # Keep track of what we have
            existing_by_image_id = {t.image_id: t for t in existing_templates}
            avatar_template = existing_by_image_id.get(0)
            
            # Process new photos
            processing_results = self.process_employee_photos(
                employee_id, new_photos_data, selected_avatar_index
            )
            
            successful_results = [r for r in processing_results if r['success']]
            
            if not successful_results:
                raise ValueError("No photos could be processed successfully")
            
            # Handle avatar update
            avatar_result = next((r for r in successful_results if r['is_primary']), None)
            
            if avatar_result:
                if avatar_template:
                    # Update existing avatar
                    self._update_template_from_result(avatar_template, avatar_result)
                    logger.info(f"Updated existing avatar for employee {employee_id}")
                else:
                    # Create new avatar
                    avatar_template = self._create_template_from_result(employee_id, avatar_result)
                    db.add(avatar_template)
                    logger.info(f"Created new avatar for employee {employee_id}")
            
            # Handle secondary templates (image_id 1,2,3)
            secondary_results = [r for r in successful_results if not r['is_primary']]
            
            # Delete old secondary templates
            for image_id in [1, 2, 3]:
                if image_id in existing_by_image_id:
                    old_template = existing_by_image_id[image_id]
                    # Delete old photo file
                    if os.path.exists(old_template.file_path):
                        os.remove(old_template.file_path)
                    db.delete(old_template)
                    logger.info(f"Deleted old template image_id {image_id} for employee {employee_id}")
            
            # Create new secondary templates
            new_templates = []
            for result in secondary_results:
                template = self._create_template_from_result(employee_id, result)
                db.add(template)
                new_templates.append(template)
                logger.info(f"Created new template image_id {result['image_id']} for employee {employee_id}")
            
            db.commit()
            
            return {
                'success': True,
                'avatar_updated': avatar_result is not None,
                'secondary_templates_created': len(new_templates),
                'total_templates': len(successful_results),
                'processing_results': processing_results
            }
            
        except Exception as e:
            logger.error(f"Error updating templates for employee {employee_id}: {e}")
            db.rollback()
            raise
    
    def _create_template_from_result(self, employee_id: str, result: Dict[str, Any]) -> FaceTemplate:
        """Helper method to create FaceTemplate from processing result"""
        return FaceTemplate(
            employee_id=employee_id,
            image_id=result['image_id'],
            filename=result['filename'],
            file_path=result['file_path'],
            embedding_vector=result['embedding'],
            is_primary=result['is_primary'],
            created_from='ADMIN_UPLOAD',
            quality_score=result['quality_score'],
            confidence_score=result['confidence_score']
        )
    
    def _update_template_from_result(self, template: FaceTemplate, result: Dict[str, Any]) -> None:
        """Helper method to update existing FaceTemplate from processing result"""
        # Delete old photo file
        if os.path.exists(template.file_path):
            os.remove(template.file_path)
        
        # Update template fields
        template.filename = result['filename']
        template.file_path = result['file_path']
        template.embedding_vector = result['embedding']
        template.quality_score = result['quality_score']
        template.confidence_score = result['confidence_score']
        template.updated_at = datetime.datetime.utcnow()
    
    def get_employee_templates(self, db: Session, employee_id: str) -> Dict[str, Any]:
        """Get all face templates for an employee"""
        try:
            templates = db.query(FaceTemplate).filter(
                FaceTemplate.employee_id == employee_id
            ).order_by(FaceTemplate.image_id).all()
            
            result = {
                'employee_id': employee_id,
                'total_templates': len(templates),
                'has_avatar': any(t.image_id == 0 for t in templates),
                'templates': []
            }
            
            for template in templates:
                template_data = {
                    'id': template.id,
                    'image_id': template.image_id,
                    'filename': template.filename,
                    'file_path': template.file_path,
                    'is_primary': template.is_primary,
                    'quality_score': template.quality_score,
                    'confidence_score': template.confidence_score,
                    'created_at': template.created_at.isoformat(),
                    'match_count': template.match_count,
                    'last_matched': template.last_matched.isoformat() if template.last_matched else None,
                    'age_days': template.age_days
                }
                result['templates'].append(template_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting templates for employee {employee_id}: {e}")
            raise
    
    def delete_employee_photos(self, db: Session, employee_id: str) -> None:
        """Delete all photos and templates for an employee"""
        try:
            # Get all templates
            templates = db.query(FaceTemplate).filter(
                FaceTemplate.employee_id == employee_id
            ).all()
            
            # Delete photo files
            for template in templates:
                if os.path.exists(template.file_path):
                    os.remove(template.file_path)
                    logger.info(f"Deleted photo file: {template.file_path}")
            
            # Delete template records
            db.query(FaceTemplate).filter(
                FaceTemplate.employee_id == employee_id
            ).delete()
            
            # Delete employee photo directory if empty
            employee_dir = self.get_employee_photo_dir(employee_id)
            if employee_dir.exists() and not any(employee_dir.iterdir()):
                employee_dir.rmdir()
                logger.info(f"Deleted empty employee directory: {employee_dir}")
            
            db.commit()
            logger.info(f"Successfully deleted all photos for employee {employee_id}")
            
        except Exception as e:
            logger.error(f"Error deleting photos for employee {employee_id}: {e}")
            db.rollback()
            raise

# Global instance
face_embedding_service = FaceEmbeddingService()
