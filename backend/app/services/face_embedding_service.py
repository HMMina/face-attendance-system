"""
Face Embedding Database Service
Handles storage and retrieval of face embeddings
Uses optimized Cosine Similarity for face matching
"""
from typing import List, Optional, Tuple
import numpy as np
from sqlalchemy.orm import Session
from app.models.face_embedding import FaceEmbedding
from app.models.employee import Employee
import logging

logger = logging.getLogger(__name__)

class CosineSimilarityUtils:
    """
    Centralized Cosine Similarity utilities for face embeddings
    Ensures consistent calculation across the entire application
    """
    
    @staticmethod
    def calculate_cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two face embeddings
        Optimized for InsightFace embeddings (512-dimensional, L2-normalized)
        
        Args:
            embedding1: First face embedding (512-dim)
            embedding2: Second face embedding (512-dim)
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        try:
            # Input validation
            if embedding1.shape != embedding2.shape:
                logger.warning(f"Embedding shape mismatch: {embedding1.shape} vs {embedding2.shape}")
                return 0.0
            
            # Calculate norms
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            # Handle edge cases
            if norm1 == 0 or norm2 == 0:
                logger.warning("Zero norm embedding detected")
                return 0.0
            
            # Normalize embeddings for numerical stability
            emb1_normalized = embedding1 / norm1
            emb2_normalized = embedding2 / norm2
            
            # Calculate cosine similarity (dot product of normalized vectors)
            similarity = np.dot(emb1_normalized, emb2_normalized)
            
            # Clamp to valid range [0, 1] for face embeddings
            # InsightFace embeddings are typically in positive space
            similarity = np.clip(similarity, 0.0, 1.0)
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Cosine similarity calculation error: {e}")
            return 0.0
    
    @staticmethod
    def batch_cosine_similarity(query_embedding: np.ndarray, 
                               embedding_list: List[np.ndarray]) -> List[float]:
        """
        Calculate cosine similarity between query and multiple embeddings
        Optimized for batch processing
        
        Args:
            query_embedding: Query face embedding
            embedding_list: List of stored embeddings
            
        Returns:
            List of similarity scores
        """
        try:
            if not embedding_list:
                return []
            
            # Convert to matrix for vectorized operations
            embedding_matrix = np.array(embedding_list)
            
            # Normalize query embedding
            query_norm = np.linalg.norm(query_embedding)
            if query_norm == 0:
                return [0.0] * len(embedding_list)
            
            query_normalized = query_embedding / query_norm
            
            # Normalize all stored embeddings
            embedding_norms = np.linalg.norm(embedding_matrix, axis=1, keepdims=True)
            # Avoid division by zero
            valid_mask = embedding_norms.flatten() > 0
            
            similarities = np.zeros(len(embedding_list))
            
            if np.any(valid_mask):
                embeddings_normalized = embedding_matrix[valid_mask] / embedding_norms[valid_mask]
                # Batch dot product
                similarities[valid_mask] = np.dot(embeddings_normalized, query_normalized)
            
            # Clamp to valid range
            similarities = np.clip(similarities, 0.0, 1.0)
            
            return similarities.tolist()
            
        except Exception as e:
            logger.error(f"Batch cosine similarity error: {e}")
            return [0.0] * len(embedding_list)

class FaceEmbeddingService:
    """Service for managing face embeddings in database"""
    
    @staticmethod
    def save_embedding(
        db: Session,
        employee_id: str,
        embedding: np.ndarray,
        face_photo_path: Optional[str] = None,
        confidence_threshold: float = 0.7,
        photo_quality: float = 0.0,
        registered_by: str = "system",
        registration_device: Optional[str] = None,
        is_primary: bool = False
    ) -> FaceEmbedding:
        """
        Save face embedding to database
        """
        try:
            # Convert numpy array to list for JSON storage
            embedding_list = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
            
            # Check if employee exists
            employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
            if not employee:
                raise ValueError(f"Employee {employee_id} not found")
            
            # If this is marked as primary, unset other primary embeddings
            if is_primary:
                db.query(FaceEmbedding).filter(
                    FaceEmbedding.employee_id == employee_id,
                    FaceEmbedding.is_primary == True
                ).update({"is_primary": False})
            
            # Create new embedding record
            face_embedding = FaceEmbedding(
                employee_id=employee_id,
                embedding_vector=embedding_list,
                face_photo_path=face_photo_path,
                confidence_threshold=confidence_threshold,
                photo_quality=photo_quality,
                registered_by=registered_by,
                registration_device=registration_device,
                is_primary=is_primary,
                is_active=True
            )
            
            db.add(face_embedding)
            db.commit()
            db.refresh(face_embedding)
            
            logger.info(f"Saved embedding for employee {employee_id}")
            return face_embedding
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving embedding: {e}")
            raise
    
    @staticmethod
    def get_employee_embeddings(
        db: Session,
        employee_id: str,
        active_only: bool = True
    ) -> List[FaceEmbedding]:
        """
        Get all embeddings for an employee
        """
        query = db.query(FaceEmbedding).filter(FaceEmbedding.employee_id == employee_id)
        
        if active_only:
            query = query.filter(FaceEmbedding.is_active == True)
        
        return query.all()
    
    @staticmethod
    def get_all_active_embeddings(db: Session) -> List[Tuple[str, np.ndarray, float]]:
        """
        Get all active embeddings for matching
        Returns: List of (employee_id, embedding_vector, confidence_threshold)
        """
        embeddings = db.query(FaceEmbedding).filter(
            FaceEmbedding.is_active == True
        ).all()
        
        result = []
        for emb in embeddings:
            try:
                # Convert list back to numpy array
                vector = np.array(emb.embedding_vector, dtype=np.float32)
                result.append((emb.employee_id, vector, emb.confidence_threshold))
            except Exception as e:
                logger.warning(f"Error converting embedding {emb.id}: {e}")
                continue
        
        return result
    
    @staticmethod
    def get_primary_embedding(db: Session, employee_id: str) -> Optional[FaceEmbedding]:
        """
        Get primary embedding for an employee
        """
        return db.query(FaceEmbedding).filter(
            FaceEmbedding.employee_id == employee_id,
            FaceEmbedding.is_primary == True,
            FaceEmbedding.is_active == True
        ).first()
    
    @staticmethod
    def update_last_used(db: Session, embedding_id: int):
        """
        Update last_used timestamp for an embedding
        """
        try:
            from datetime import datetime
            db.query(FaceEmbedding).filter(FaceEmbedding.id == embedding_id).update({
                "last_used": datetime.utcnow()
            })
            db.commit()
        except Exception as e:
            logger.error(f"Error updating last_used: {e}")
            db.rollback()
    
    @staticmethod
    def deactivate_embedding(db: Session, embedding_id: int):
        """
        Deactivate an embedding
        """
        try:
            db.query(FaceEmbedding).filter(FaceEmbedding.id == embedding_id).update({
                "is_active": False
            })
            db.commit()
            logger.info(f"Deactivated embedding {embedding_id}")
        except Exception as e:
            logger.error(f"Error deactivating embedding: {e}")
            db.rollback()
    
    @staticmethod
    def delete_employee_embeddings(db: Session, employee_id: str):
        """
        Delete all embeddings for an employee
        """
        try:
            deleted = db.query(FaceEmbedding).filter(
                FaceEmbedding.employee_id == employee_id
            ).delete()
            db.commit()
            logger.info(f"Deleted {deleted} embeddings for employee {employee_id}")
            return deleted
        except Exception as e:
            logger.error(f"Error deleting embeddings: {e}")
            db.rollback()
            raise
    
    @staticmethod
    def calculate_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings
        Uses centralized CosineSimilarityUtils for consistency
        """
        return CosineSimilarityUtils.calculate_cosine_similarity(embedding1, embedding2)
    
    @staticmethod
    def find_best_match(
        db: Session,
        query_embedding: np.ndarray,
        min_threshold: float = 0.7,
        use_batch_processing: bool = True
    ) -> Tuple[Optional[str], float, Optional[int]]:
        """
        Find best matching employee for a given embedding using optimized Cosine Similarity
        
        Args:
            db: Database session
            query_embedding: Query face embedding (512-dim)
            min_threshold: Minimum cosine similarity threshold
            use_batch_processing: Whether to use optimized batch processing
            
        Returns: (employee_id, confidence, embedding_id) or (None, 0.0, None)
        """
        try:
            # Get all active embeddings
            embeddings = db.query(FaceEmbedding).filter(
                FaceEmbedding.is_active == True
            ).all()
            
            if not embeddings:
                logger.info("No active embeddings found in database")
                return None, 0.0, None
            
            best_match = None
            best_similarity = 0.0
            best_embedding_id = None
            
            if use_batch_processing and len(embeddings) > 1:
                # Optimized batch processing for multiple embeddings
                try:
                    stored_embeddings = []
                    embedding_metadata = []
                    
                    for emb in embeddings:
                        try:
                            stored_embedding = np.array(emb.embedding_vector, dtype=np.float32)
                            stored_embeddings.append(stored_embedding)
                            embedding_metadata.append((emb.employee_id, emb.id, emb.confidence_threshold))
                        except Exception as e:
                            logger.warning(f"Error processing embedding {emb.id}: {e}")
                            continue
                    
                    if stored_embeddings:
                        # Batch calculate similarities
                        similarities = CosineSimilarityUtils.batch_cosine_similarity(
                            query_embedding, stored_embeddings
                        )
                        
                        # Find best match
                        for i, (employee_id, emb_id, individual_threshold) in enumerate(embedding_metadata):
                            similarity = similarities[i]
                            threshold = max(min_threshold, individual_threshold)
                            
                            if similarity > best_similarity and similarity >= threshold:
                                best_similarity = similarity
                                best_match = employee_id
                                best_embedding_id = emb_id
                    
                except Exception as e:
                    logger.warning(f"Batch processing failed, falling back to individual processing: {e}")
                    use_batch_processing = False
            
            if not use_batch_processing:
                # Individual processing fallback
                for emb in embeddings:
                    try:
                        # Convert stored embedding to numpy array
                        stored_embedding = np.array(emb.embedding_vector, dtype=np.float32)
                        
                        # Calculate similarity using centralized method
                        similarity = CosineSimilarityUtils.calculate_cosine_similarity(
                            query_embedding, stored_embedding
                        )
                        
                        # Use individual threshold if higher than minimum
                        threshold = max(min_threshold, emb.confidence_threshold)
                        
                        if similarity > best_similarity and similarity >= threshold:
                            best_similarity = similarity
                            best_match = emb.employee_id
                            best_embedding_id = emb.id
                            
                    except Exception as e:
                        logger.warning(f"Error processing embedding {emb.id}: {e}")
                        continue
            
            # Update last_used for the matched embedding
            if best_embedding_id:
                FaceEmbeddingService.update_last_used(db, best_embedding_id)
                logger.info(f"Best match found: {best_match} with similarity {best_similarity:.3f}")
            else:
                logger.info(f"No match found above threshold {min_threshold}")
            
            return best_match, best_similarity, best_embedding_id
            
        except Exception as e:
            logger.error(f"Error finding best match: {e}")
            return None, 0.0, None
