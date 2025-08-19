"""
Employee Photo Storage Service
Manages local storage of employee photos for face recognition
"""
import os
import uuid
import shutil
from typing import List, Optional, Dict
from pathlib import Path
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class EmployeePhotoService:
    """Service to manage employee photos stored locally"""
    
    def __init__(self, base_storage_path: str = None):
        if base_storage_path is None:
            # Default to project data directory
            project_root = Path(__file__).parent.parent.parent
            self.storage_path = project_root / "data" / "employee_photos"
        else:
            self.storage_path = Path(base_storage_path)
        
        # Create directory if it doesn't exist
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Supported image formats
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        
        logger.info(f"EmployeePhotoService initialized with storage: {self.storage_path}")
    
    def save_employee_photo(self, employee_id: str, image_file, original_filename: str = None) -> Dict[str, str]:
        """
        Save employee photo to local storage
        
        Args:
            employee_id: Unique employee identifier
            image_file: Image file object or path
            original_filename: Original filename for reference
            
        Returns:
            Dict with photo info including local path
        """
        try:
            # Create employee directory
            employee_dir = self.storage_path / employee_id
            employee_dir.mkdir(exist_ok=True)
            
            # Generate unique filename
            photo_id = str(uuid.uuid4())
            file_extension = self._get_file_extension(original_filename or "photo.jpg")
            
            # Create filenames
            original_filename_local = f"{photo_id}_original{file_extension}"
            processed_filename_local = f"{photo_id}_processed{file_extension}"
            
            original_path = employee_dir / original_filename_local
            processed_path = employee_dir / processed_filename_local
            
            # Save original image
            if hasattr(image_file, 'save'):
                # PIL Image object
                image_file.save(original_path, quality=95)
                processed_image = image_file.copy()
            elif hasattr(image_file, 'read'):
                # File-like object
                with open(original_path, 'wb') as f:
                    shutil.copyfileobj(image_file, f)
                # Open for processing
                processed_image = Image.open(original_path)
            else:
                # File path
                shutil.copy2(image_file, original_path)
                processed_image = Image.open(original_path)
            
            # Create processed version (standardized for face recognition)
            processed_image = self._process_image_for_recognition(processed_image)
            processed_image.save(processed_path, quality=95)
            
            # Create thumbnail
            thumbnail_path = employee_dir / f"{photo_id}_thumb{file_extension}"
            thumbnail = processed_image.copy()
            thumbnail.thumbnail((150, 150), Image.Resampling.LANCZOS)
            thumbnail.save(thumbnail_path, quality=85)
            
            photo_info = {
                "photo_id": photo_id,
                "employee_id": employee_id,
                "original_path": str(original_path),
                "processed_path": str(processed_path),
                "thumbnail_path": str(thumbnail_path),
                "original_filename": original_filename,
                "file_size": original_path.stat().st_size,
                "image_format": file_extension.upper().replace('.', ''),
                "dimensions": f"{processed_image.width}x{processed_image.height}"
            }
            
            logger.info(f"Saved photo for employee {employee_id}: {photo_id}")
            return photo_info
            
        except Exception as e:
            logger.error(f"Error saving photo for employee {employee_id}: {e}")
            raise Exception(f"Failed to save employee photo: {str(e)}")
    
    def get_employee_photos(self, employee_id: str) -> List[Dict[str, str]]:
        """Get all photos for an employee"""
        try:
            employee_dir = self.storage_path / employee_id
            if not employee_dir.exists():
                return []
            
            photos = []
            # Look for original files
            for original_file in employee_dir.glob("*_original.*"):
                photo_id = original_file.stem.split('_original')[0]
                file_extension = original_file.suffix
                
                processed_path = employee_dir / f"{photo_id}_processed{file_extension}"
                thumbnail_path = employee_dir / f"{photo_id}_thumb{file_extension}"
                
                photo_info = {
                    "photo_id": photo_id,
                    "employee_id": employee_id,
                    "original_path": str(original_file),
                    "processed_path": str(processed_path) if processed_path.exists() else None,
                    "thumbnail_path": str(thumbnail_path) if thumbnail_path.exists() else None,
                    "file_size": original_file.stat().st_size if original_file.exists() else 0,
                    "created_at": original_file.stat().st_ctime if original_file.exists() else None
                }
                photos.append(photo_info)
            
            return sorted(photos, key=lambda x: x['created_at'] or 0, reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting photos for employee {employee_id}: {e}")
            return []
    
    def get_employee_recognition_photos(self, employee_id: str) -> List[str]:
        """Get processed photos suitable for face recognition"""
        try:
            employee_dir = self.storage_path / employee_id
            if not employee_dir.exists():
                return []
            
            processed_photos = []
            for processed_file in employee_dir.glob("*_processed.*"):
                if processed_file.exists():
                    processed_photos.append(str(processed_file))
            
            return processed_photos
            
        except Exception as e:
            logger.error(f"Error getting recognition photos for employee {employee_id}: {e}")
            return []
    
    def delete_employee_photo(self, employee_id: str, photo_id: str) -> bool:
        """Delete a specific photo"""
        try:
            employee_dir = self.storage_path / employee_id
            if not employee_dir.exists():
                return False
            
            # Delete all variants of the photo
            deleted_any = False
            for suffix in ['_original', '_processed', '_thumb']:
                for ext in self.supported_formats:
                    photo_file = employee_dir / f"{photo_id}{suffix}{ext}"
                    if photo_file.exists():
                        photo_file.unlink()
                        deleted_any = True
            
            logger.info(f"Deleted photo {photo_id} for employee {employee_id}")
            return deleted_any
            
        except Exception as e:
            logger.error(f"Error deleting photo {photo_id} for employee {employee_id}: {e}")
            return False
    
    def delete_all_employee_photos(self, employee_id: str) -> bool:
        """Delete all photos for an employee"""
        try:
            employee_dir = self.storage_path / employee_id
            if employee_dir.exists():
                shutil.rmtree(employee_dir)
                logger.info(f"Deleted all photos for employee {employee_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting all photos for employee {employee_id}: {e}")
            return False
    
    def get_storage_stats(self) -> Dict[str, any]:
        """Get storage statistics"""
        try:
            total_size = 0
            total_photos = 0
            employee_count = 0
            
            for employee_dir in self.storage_path.iterdir():
                if employee_dir.is_dir():
                    employee_count += 1
                    for photo_file in employee_dir.glob("*_original.*"):
                        if photo_file.exists():
                            total_size += photo_file.stat().st_size
                            total_photos += 1
            
            return {
                "total_employees": employee_count,
                "total_photos": total_photos,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "storage_path": str(self.storage_path)
            }
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            return {}
    
    def _get_file_extension(self, filename: str) -> str:
        """Get file extension from filename"""
        if not filename:
            return '.jpg'
        
        ext = Path(filename).suffix.lower()
        if ext in self.supported_formats:
            return ext
        return '.jpg'  # Default to jpg
    
    def _process_image_for_recognition(self, image: Image.Image) -> Image.Image:
        """Process image for optimal face recognition"""
        try:
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large (max 1024px on longest side)
            max_size = 1024
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
                new_size = tuple(int(dim * ratio) for dim in image.size)
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return image  # Return original if processing fails

# Global instance
photo_service = EmployeePhotoService()
