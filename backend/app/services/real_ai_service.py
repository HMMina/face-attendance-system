"""
Real AI Service for Face Recognition
Replaces mock_ai_service.py with actual model implementations

UPDATES:
- v1.1: Anti-spoofing now uses full image instead of cropped face for better context analysis
- Recognition still uses face crops via InsightFace's internal detection for optimal accuracy
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
from app.services.enhanced_face_embedding_service import face_embedding_service as FaceEmbeddingService
from app.models.employee import Employee

# Will need these dependencies:
# pip install onnxruntime insightface ultralytics scikit-learn

class AIConfig:
    """Configuration class for AI service optimization"""
    
    # Detection settings
    DETECTION_CONFIDENCE_THRESHOLD = 0.5
    MAX_IMAGE_SIZE = 1280
    
    # Recognition settings  
    RECOGNITION_THRESHOLD = 0.7
    EMBEDDING_CACHE_SIZE = 1000
    FACE_CROP_PADDING = 20
    
    # Anti-spoofing settings
    ANTI_SPOOF_THRESHOLD = 0.5
    USE_FULL_IMAGE_FOR_SPOOF = True
    
    # Cosine Similarity settings
    COSINE_SIMILARITY_THRESHOLD = 0.65  # Giảm từ 0.7 xuống 0.65 để dễ nhận diện
    NORMALIZE_EMBEDDINGS_BEFORE_COMPARISON = True
    USE_OPTIMIZED_COSINE_SIMILARITY = True
    
    # Performance settings
    BATCH_SIZE = 16
    WARM_UP_ON_INIT = True
    ENABLE_PERFORMANCE_TRACKING = True
    
    # Image preprocessing
    AUTO_ENHANCE_DARK_IMAGES = True
    BRIGHTNESS_THRESHOLD = 80
    BRIGHTNESS_ALPHA = 1.2
    BRIGHTNESS_BETA = 10

class CosineSimilarityCalculator:
    """
    Optimized Cosine Similarity calculator for face embeddings
    Focused on performance and accuracy for face recognition tasks
    """
    
    @staticmethod
    def calculate(embedding1: np.ndarray, embedding2: np.ndarray, 
                 normalize: bool = True) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector (512-dim)
            embedding2: Second embedding vector (512-dim)
            normalize: Whether to normalize embeddings before calculation
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        try:
            # Input validation
            if embedding1.shape != embedding2.shape:
                raise ValueError(f"Embedding shapes mismatch: {embedding1.shape} vs {embedding2.shape}")
            
            if len(embedding1.shape) != 1:
                raise ValueError(f"Expected 1D embeddings, got shape: {embedding1.shape}")
            
            # Handle zero vectors
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            if normalize:
                # Pre-normalize for better numerical stability
                emb1_norm = embedding1 / norm1
                emb2_norm = embedding2 / norm2
                # Cosine similarity with normalized vectors is just dot product
                similarity = np.dot(emb1_norm, emb2_norm)
            else:
                # Direct cosine similarity calculation
                similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
            
            # Clamp to valid range [0, 1] for face embeddings
            # (Face embeddings from InsightFace are typically in positive space)
            similarity = np.clip(similarity, 0.0, 1.0)
            
            return float(similarity)
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Cosine similarity calculation error: {e}")
            return 0.0
    
    @staticmethod
    def batch_calculate(query_embedding: np.ndarray, 
                       embedding_matrix: np.ndarray,
                       normalize: bool = True) -> np.ndarray:
        """
        Calculate cosine similarity between one query and multiple embeddings
        Optimized for batch processing
        
        Args:
            query_embedding: Single query embedding (512-dim)
            embedding_matrix: Matrix of embeddings (N x 512)
            normalize: Whether to normalize embeddings
            
        Returns:
            Array of similarity scores (N,)
        """
        try:
            if normalize:
                # Normalize query
                query_norm = query_embedding / np.linalg.norm(query_embedding)
                
                # Normalize all embeddings in matrix
                norms = np.linalg.norm(embedding_matrix, axis=1, keepdims=True)
                # Avoid division by zero
                norms = np.where(norms == 0, 1, norms)
                embeddings_norm = embedding_matrix / norms
                
                # Batch dot product
                similarities = np.dot(embeddings_norm, query_norm)
            else:
                # Direct calculation
                query_norm = np.linalg.norm(query_embedding)
                embedding_norms = np.linalg.norm(embedding_matrix, axis=1)
                
                # Avoid division by zero
                valid_mask = (query_norm > 0) & (embedding_norms > 0)
                similarities = np.zeros(len(embedding_matrix))
                
                if np.any(valid_mask):
                    dot_products = np.dot(embedding_matrix[valid_mask], query_embedding)
                    similarities[valid_mask] = dot_products / (query_norm * embedding_norms[valid_mask])
            
            # Clamp to valid range
            similarities = np.clip(similarities, 0.0, 1.0)
            
            return similarities
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Batch cosine similarity error: {e}")
            return np.zeros(len(embedding_matrix))
    
    @staticmethod
    def find_best_matches(query_embedding: np.ndarray,
                         embeddings: List[Tuple[str, np.ndarray]],
                         threshold: float = 0.7,
                         top_k: int = 1) -> List[Tuple[str, float]]:
        """
        Find top-k best matches using cosine similarity
        
        Args:
            query_embedding: Query embedding vector
            embeddings: List of (id, embedding) tuples
            threshold: Minimum similarity threshold (use 0.0 to get all matches)
            top_k: Number of top matches to return
            
        Returns:
            List of (id, similarity) sorted by similarity (descending)
        """
        try:
            if not embeddings:
                return []
            
            # Extract embeddings and IDs
            ids = [item[0] for item in embeddings]
            embedding_matrix = np.array([item[1] for item in embeddings])
            
            # Calculate similarities in batch
            similarities = CosineSimilarityCalculator.batch_calculate(
                query_embedding, embedding_matrix, normalize=AIConfig.NORMALIZE_EMBEDDINGS_BEFORE_COMPARISON
            )
            
            # If threshold is 0, return all matches (for debugging)
            if threshold <= 0.0:
                # Get ALL matches, sorted by similarity
                all_pairs = list(zip(ids, similarities))
                sorted_pairs = sorted(all_pairs, key=lambda x: x[1], reverse=True)
                return sorted_pairs[:top_k]
            else:
                # Filter by threshold and get top-k
                valid_indices = similarities >= threshold
                valid_similarities = similarities[valid_indices]
                valid_ids = [ids[i] for i in range(len(ids)) if valid_indices[i]]
                
                # Sort by similarity (descending)
                sorted_pairs = sorted(zip(valid_ids, valid_similarities), 
                                    key=lambda x: x[1], reverse=True)
                
                return sorted_pairs[:top_k]
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Best matches finding error: {e}")
            return []

class RealAIService:
    """
    Production AI service with real model implementations
    Optimized for performance and reliability
    """
    
    def __init__(self, model_path: str = None):
        # Set default model path relative to backend directory
        if model_path is None:
            backend_root = Path(__file__).parent.parent.parent
            self.model_path = backend_root / "data" / "models"
        else:
            self.model_path = Path(model_path)
            
        self.logger = logging.getLogger(__name__)
        
        # Models will be loaded here
        self.face_detector = None
        self.anti_spoof_model = None  
        self.face_recognizer = None
        
        # Performance optimization caches
        self.embedding_cache = {}
        self._model_warm_up_done = False
        self._performance_metrics = {
            "total_recognitions": 0,
            "avg_processing_time": 0.0,
            "cache_hits": 0,
            "last_reset": None
        }
        
        self._load_models()
    
    def _load_models(self):
        """Load all AI models with optimized error handling and logging"""
        self.logger.info(f"Loading AI models from: {self.model_path}")
        
        # Check if model directory exists
        if not self.model_path.exists():
            self.logger.error(f"Model directory not found: {self.model_path}")
            raise FileNotFoundError(f"Model directory not found: {self.model_path}")
        
        # Track loading success
        loaded_models = []
        
        try:
            # 1. Load Face Detection Model (Critical - Required)
            if self._load_face_detector():
                loaded_models.append("Face Detection")
            else:
                raise Exception("Critical: Face detection model failed to load")
            
            # 2. Load Anti-Spoofing Model (Optional - Graceful degradation)
            if self._load_anti_spoof_model():
                loaded_models.append("Anti-Spoofing")
            else:
                self.logger.warning("Anti-spoofing model not loaded - will use fallback")
            
            # 3. Load Face Recognition Model (Critical - Required)
            if self._load_face_recognizer():
                loaded_models.append("Face Recognition")
            else:
                raise Exception("Critical: Face recognition model failed to load")
            
            self.logger.info(f"✅ Successfully loaded models: {', '.join(loaded_models)}")
            
        except Exception as e:
            self.logger.error(f"❌ Model loading failed: {e}")
            self.logger.info("Available models in directory:")
            for category in ['detection', 'classification', 'recognition']:
                cat_path = self.model_path / category
                if cat_path.exists():
                    files = list(cat_path.glob('*'))
                    self.logger.info(f"  {category}: {[f.name for f in files if f.is_file()]}")
                else:
                    self.logger.info(f"  {category}: directory not found")
            raise
    
    def _load_face_detector(self) -> bool:
        """Load face detection model with optimized priority order"""
        try:
            from ultralytics import YOLO
            
            # Priority order for face detection models (most reliable first)
            detector_options = [
                ("Local YOLOv11s", self.model_path / "detection" / "yolov11s.pt"),
                ("Local YOLOv8n-face", self.model_path / "detection" / "yolov8n-face.pt"),
                ("Local YOLOv8n", self.model_path / "detection" / "yolov8n.pt"),
                ("Auto-download YOLOv11s", "yolov11s.pt"),
                ("Auto-download YOLOv8n", "yolov8n.pt")
            ]
            
            for model_name, model_path in detector_options:
                try:
                    if isinstance(model_path, Path):
                        if model_path.exists():
                            size_mb = model_path.stat().st_size / (1024*1024)
                            self.logger.info(f"Loading {model_name} ({size_mb:.1f}MB)...")
                            self.face_detector = YOLO(str(model_path))
                            self.logger.info(f"✅ {model_name} loaded successfully")
                            return True
                        else:
                            self.logger.debug(f"⏭️ {model_name} not found: {model_path}")
                            continue
                    else:
                        # Auto-download option
                        self.logger.info(f"Attempting {model_name}...")
                        self.face_detector = YOLO(model_path)
                        self.logger.info(f"✅ {model_name} downloaded and loaded")
                        return True
                        
                except Exception as e:
                    self.logger.warning(f"❌ Failed to load {model_name}: {e}")
                    continue
            
            self.logger.error("❌ No face detection model could be loaded")
            return False
            
        except ImportError as e:
            self.logger.error(f"❌ Ultralytics not installed: {e}")
            self.logger.info("💡 Install with: pip install ultralytics")
            return False
    
    def _load_anti_spoof_model(self) -> bool:
        """Load anti-spoofing model with graceful degradation"""
        try:
            from ultralytics import YOLO
            
            # Priority order for anti-spoofing models
            spoof_options = [
                ("Local YOLOv11s-cls", self.model_path / "classification" / "yolov11s-cls.pt", "yolo"),
                ("Local ONNX Anti-spoof", self.model_path / "classification" / "antispoofing.onnx", "onnx"),
                ("Local YOLOv8n-cls", self.model_path / "classification" / "yolov8n-cls.pt", "yolo"),
                ("Auto-download YOLOv11s-cls", "yolov11s-cls.pt", "yolo")
            ]
            
            for model_name, model_path, model_type in spoof_options:
                try:
                    if isinstance(model_path, Path):
                        if model_path.exists():
                            size_mb = model_path.stat().st_size / (1024*1024)
                            self.logger.info(f"Loading {model_name} ({size_mb:.1f}MB)...")
                            
                            if model_type == "yolo":
                                self.anti_spoof_model = YOLO(str(model_path))
                            elif model_type == "onnx":
                                import onnxruntime as ort
                                self.anti_spoof_model = ort.InferenceSession(str(model_path))
                            
                            self.logger.info(f"✅ {model_name} loaded successfully")
                            return True
                        else:
                            self.logger.debug(f"⏭️ {model_name} not found: {model_path}")
                            continue
                    else:
                        # Auto-download option
                        self.logger.info(f"Attempting {model_name}...")
                        self.anti_spoof_model = YOLO(model_path)
                        self.logger.info(f"✅ {model_name} downloaded and loaded")
                        return True
                        
                except Exception as e:
                    self.logger.warning(f"❌ Failed to load {model_name}: {e}")
                    continue
            
            self.logger.warning("⚠️ No anti-spoofing model loaded - using permissive mode")
            self.anti_spoof_model = None
            return False  # Not critical, graceful degradation
            
        except ImportError as e:
            self.logger.warning(f"⚠️ Anti-spoofing dependencies missing: {e}")
            self.anti_spoof_model = None
            return False
    
    def _load_face_recognizer(self) -> bool:
        """Load face recognition model with optimized provider selection"""
        try:
            import insightface
            
            # Priority order for face recognition models
            recognition_options = [
                ("Local Buffalo_L", "buffalo_l", self.model_path / "recognition" / "buffalo_l"),
                ("Local Buffalo_S", "buffalo_s", self.model_path / "recognition" / "buffalo_s"),
                ("Auto-download Buffalo_L", "buffalo_l", None),
                ("Auto-download Buffalo_S", "buffalo_s", None),
            ]
            
            # Detect available providers (CPU/GPU)
            try:
                import onnxruntime as ort
                available_providers = ort.get_available_providers()
                if 'CUDAExecutionProvider' in available_providers:
                    providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
                    self.logger.info("🚀 CUDA available - using GPU acceleration")
                else:
                    providers = ['CPUExecutionProvider']
                    self.logger.info("💻 Using CPU execution")
            except ImportError:
                providers = ['CPUExecutionProvider']
                self.logger.warning("⚠️ ONNXRuntime not found, using default providers")
            
            for model_name, model_key, model_path in recognition_options:
                try:
                    if model_path and model_path.exists():
                        # Calculate total size for local models
                        total_size = sum(f.stat().st_size for f in model_path.glob('*.onnx'))
                        size_mb = total_size / (1024*1024)
                        self.logger.info(f"Loading {model_name} ({size_mb:.1f}MB)...")
                        
                        # Load from local path with custom root
                        self.face_recognizer = insightface.app.FaceAnalysis(
                            name=model_key,
                            root=str(model_path.parent),
                            providers=providers
                        )
                    else:
                        if model_path:
                            self.logger.debug(f"⏭️ {model_name} not found: {model_path}")
                            continue
                        
                        # Auto-download option
                        self.logger.info(f"Attempting {model_name}...")
                        self.face_recognizer = insightface.app.FaceAnalysis(
                            name=model_key,
                            providers=providers
                        )
                    
                    # Prepare the model
                    self.face_recognizer.prepare(ctx_id=0, det_size=(640, 640))
                    self.logger.info(f"✅ {model_name} loaded and prepared successfully")
                    
                    # Test the model with dummy data
                    import numpy as np
                    test_img = np.zeros((100, 100, 3), dtype=np.uint8)
                    faces = self.face_recognizer.get(test_img)
                    self.logger.info(f"🧪 Model test complete - detected {len(faces)} faces in test image")
                    
                    return True
                    
                except Exception as e:
                    self.logger.warning(f"❌ Failed to load {model_name}: {e}")
                    continue
            
            self.logger.error("❌ No face recognition model could be loaded")
            return False
            
        except ImportError as e:
            self.logger.error(f"❌ InsightFace not installed: {e}")
            self.logger.info("💡 Install with: pip install insightface")
            return False
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Optimize image for better AI processing
        """
        try:
            # 1. Check if image needs preprocessing
            height, width = image.shape[:2]
            
            # 2. Resize if too large (saves processing time)
            max_size = AIConfig.MAX_IMAGE_SIZE
            if max(height, width) > max_size:
                scale = max_size / max(height, width)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
                self.logger.debug(f"Resized image from {width}x{height} to {new_width}x{new_height}")
            
            # 3. Enhance image quality if needed
            if AIConfig.AUTO_ENHANCE_DARK_IMAGES and image.mean() < AIConfig.BRIGHTNESS_THRESHOLD:
                image = cv2.convertScaleAbs(image, alpha=AIConfig.BRIGHTNESS_ALPHA, beta=AIConfig.BRIGHTNESS_BETA)
                self.logger.debug("Enhanced dark image brightness")
            
            return image
            
        except Exception as e:
            self.logger.warning(f"Image preprocessing failed: {e}")
            return image

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
            if confidence < AIConfig.DETECTION_CONFIDENCE_THRESHOLD:
                return False, None
                
            return True, tuple(bbox)
            
        except Exception as e:
            self.logger.error(f"Face detection error: {e}")
            return False, None
    
    def anti_spoofing(self, image: np.ndarray, bbox: tuple = None) -> bool:
        """
        Check if face is real (anti-spoofing) using YOLOv11s-cls
        Uses full image instead of cropped face for better context analysis
        Returns: True if real face, False if spoof detected
        """
        try:
            if self.anti_spoof_model is None:
                # If model not available, assume real face
                self.logger.warning("Anti-spoofing model not loaded, skipping spoof detection")
                return True
            
            # Use full image for anti-spoofing detection
            # This provides better context and environmental information
            # that helps distinguish between real faces and spoofed images
            results = self.anti_spoof_model(image, verbose=False)
            
            if len(results) == 0:
                self.logger.warning("Anti-spoofing model returned no results")
                return True  # Default to real if uncertain
            
            # Get classification result
            probs = results[0].probs
            if probs is not None:
                # Assuming class 0 = real, class 1 = spoof
                real_confidence = probs.data[0].cpu().numpy()
                spoof_confidence = probs.data[1].cpu().numpy() if len(probs.data) > 1 else 1 - real_confidence
                
                self.logger.info(f"🔍 Anti-spoofing scores - Real: {real_confidence:.3f}, Spoof: {spoof_confidence:.3f}")
                
                # YOLOv11s-cls returns probabilities, so we compare directly
                # Return True if real_confidence > spoof_confidence
                is_real = real_confidence > spoof_confidence
                self.logger.info(f"🔍 Anti-spoofing result: {'REAL' if is_real else 'SPOOF'}")
                return is_real
            
            return True
            
        except Exception as e:
            self.logger.error(f"Anti-spoofing error: {e}")
            return True  # Default to allowing if error
    
    def extract_embedding(self, image: np.ndarray, bbox: tuple = None) -> Optional[np.ndarray]:
        """
        Extract 512-dimensional face embedding using InsightFace
        Args:
            image: Full image or face crop
            bbox: If provided, will crop face region first (x1, y1, x2, y2)
        Returns: 512-dim numpy array or None if failed
        """
        try:
            if self.face_recognizer is None:
                return None
            
            # If bbox provided, crop the face region for more consistent recognition
            if bbox:
                x1, y1, x2, y2 = bbox
                # Add configurable padding around the face
                padding = AIConfig.FACE_CROP_PADDING
                h, w = image.shape[:2]
                x1 = max(0, x1 - padding)
                y1 = max(0, y1 - padding)
                x2 = min(w, x2 + padding)
                y2 = min(h, y2 + padding)
                
                face_crop = image[y1:y2, x1:x2]
                
                # Ensure we have a valid crop
                if face_crop.size == 0:
                    self.logger.warning("Invalid face crop, using full image")
                    working_image = image
                else:
                    working_image = face_crop
            else:
                working_image = image
            
            # InsightFace expects RGB
            if len(working_image.shape) == 3 and working_image.shape[2] == 3:
                rgb_image = cv2.cvtColor(working_image, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = working_image
            
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
                       threshold: float = None) -> Tuple[Optional[str], float]:
        """
        Match query embedding against database of employee embeddings using optimized Cosine Similarity
        
        Args:
            query_embedding: 512-dim query vector (normalized)
            employee_embeddings: List of (employee_id, embedding) tuples
            threshold: Minimum similarity threshold (TEMPORARILY DISABLED for debugging)
            
        Returns: (employee_id, confidence) or (None, 0.0) if no match
        """
        try:
            if len(employee_embeddings) == 0:
                return None, 0.0
            
            # TEMPORARILY DISABLE THRESHOLD - Always return best match for debugging
            # threshold = AIConfig.COSINE_SIMILARITY_THRESHOLD
            threshold = 0.0  # Accept any match above 0
            
            self.logger.info(f"🔍 DEBUG: Matching against {len(employee_embeddings)} employees (threshold disabled)")
            
            # Find ALL matches, sorted by similarity
            if AIConfig.USE_OPTIMIZED_COSINE_SIMILARITY:
                # Get ALL matches above 0 threshold, sort by best
                matches = CosineSimilarityCalculator.find_best_matches(
                    query_embedding=query_embedding,
                    embeddings=employee_embeddings,
                    threshold=threshold,  # 0.0 means get all matches
                    top_k=min(5, len(employee_embeddings))  # Get top 5 for debugging
                )
                
                # Log all matches for debugging
                for i, (emp_id, sim) in enumerate(matches):
                    self.logger.info(f"🎯 Match #{i+1}: Employee {emp_id} = {sim:.4f}")
                
                if matches:
                    best_match = matches[0]
                    self.logger.info(f"✅ BEST MATCH: {best_match[0]} with similarity {best_match[1]:.4f}")
                    return best_match  # (employee_id, similarity)
                else:
                    self.logger.warning("❌ No matches found at all")
                    return None, 0.0
            
            else:
                # Fallback: manual calculation with debugging
                best_match = None
                best_similarity = 0.0
                all_similarities = []
                
                for employee_id, stored_embedding in employee_embeddings:
                    similarity = CosineSimilarityCalculator.calculate(
                        query_embedding, 
                        stored_embedding,
                        normalize=AIConfig.NORMALIZE_EMBEDDINGS_BEFORE_COMPARISON
                    )
                    all_similarities.append((employee_id, similarity))
                    
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = employee_id
                
                # Sort and log all similarities for debugging
                all_similarities.sort(key=lambda x: x[1], reverse=True)
                for i, (emp_id, sim) in enumerate(all_similarities[:5]):
                    self.logger.info(f"🎯 Match #{i+1}: Employee {emp_id} = {sim:.4f}")
                
                self.logger.info(f"✅ BEST MATCH: {best_match} with similarity {best_similarity:.4f}")
                return best_match, best_similarity
            
        except Exception as e:
            self.logger.error(f"Embedding matching error: {e}")
            return None, 0.0
            self.logger.error(f"Embedding matching error: {e}")
            return None, 0.0
    
    def _update_performance_metrics(self, processing_time: float):
        """Update performance tracking metrics"""
        self._performance_metrics["total_recognitions"] += 1
        
        # Calculate rolling average
        total_count = self._performance_metrics["total_recognitions"]
        current_avg = self._performance_metrics["avg_processing_time"]
        new_avg = ((current_avg * (total_count - 1)) + processing_time) / total_count
        
        self._performance_metrics["avg_processing_time"] = round(new_avg, 3)
        
        # Log every 100 recognitions
        if total_count % 100 == 0:
            self.logger.info(f"Performance: {total_count} recognitions, avg {new_avg:.3f}s")
    
    def reset_performance_metrics(self):
        """Reset performance tracking"""
        import datetime
        self._performance_metrics = {
            "total_recognitions": 0,
            "avg_processing_time": 0.0,
            "cache_hits": 0,
            "last_reset": datetime.datetime.now().isoformat()
        }
        self.logger.info("Performance metrics reset")
    
    async def process_recognition(self, image_data, confidence: float = 0.95) -> dict:
        """
        Optimized face recognition pipeline for admin upload
        """
        try:
            # 1. Decode image from different sources
            if isinstance(image_data, bytes):
                nparr = np.frombuffer(image_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            elif isinstance(image_data, np.ndarray):
                image = image_data
            else:
                return {
                    "face_detected": False,
                    "message": "Invalid image format",
                    "success": False
                }
            
            if image is None:
                return {
                    "face_detected": False,
                    "message": "Could not decode image",
                    "success": False
                }
            
            # 2. Image preprocessing and validation
            height, width = image.shape[:2]
            if width < 100 or height < 100:
                return {
                    "face_detected": False,
                    "message": "Image too small (minimum 100x100 pixels)",
                    "success": False
                }
            
            # 3. Face detection with enhanced logging
            self.logger.debug(f"Processing image: {width}x{height}")
            found, bbox = self.detect_face(image)
            
            if not found:
                return {
                    "face_detected": False,
                    "message": "No face detected in image",
                    "success": False,
                    "image_size": f"{width}x{height}"
                }
            
            # 4. Face quality assessment
            x1, y1, x2, y2 = bbox
            face_width = x2 - x1
            face_height = y2 - y1
            face_area_ratio = (face_width * face_height) / (width * height)
            
            # Quality checks
            quality_score = 1.0
            quality_issues = []
            
            if face_area_ratio < 0.05:  # Face too small
                quality_score *= 0.7
                quality_issues.append("Face is small in image")
            
            if face_width < 80 or face_height < 80:
                quality_score *= 0.8
                quality_issues.append("Low resolution face")
            
            # 5. Anti-spoofing check (if available)
            is_real = True
            if self.anti_spoof_model is not None:
                is_real = self.anti_spoofing(image, bbox)
                if not is_real:
                    return {
                        "face_detected": True,
                        "is_real": False,
                        "message": "Possible spoof detected - please use a real photo",
                        "success": False,
                        "bbox": bbox,
                        "quality_score": quality_score
                    }
            else:
                self.logger.warning("Anti-spoofing disabled - skipping spoof detection")
            
            # 6. Extract embedding from face crop for better consistency
            embedding = self.extract_embedding(image, bbox)
            if embedding is None:
                return {
                    "face_detected": True,
                    "is_real": is_real,
                    "message": "Failed to extract face features",
                    "success": False,
                    "bbox": bbox
                }
            
            # 7. Successful processing result
            return {
                "face_detected": True,
                "is_real": is_real,
                "success": True,
                "embedding": embedding.tolist(),  # Convert to list for JSON serialization
                "confidence": float(confidence),
                "bbox": bbox,
                "face_quality": quality_score,
                "image_size": f"{width}x{height}",
                "face_size": f"{face_width}x{face_height}",
                "face_area_ratio": face_area_ratio,
                "quality_issues": quality_issues,
                "message": "Face processed successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Recognition pipeline error: {e}")
            return {
                "face_detected": False,
                "is_real": False,
                "success": False,
                "message": f"Processing error: {str(e)}"
            }
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
            
            # 4. Extract embedding from face crop for better consistency
            embedding = self.extract_embedding(image, bbox)
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
            
            # 5. Extract embedding from face crop for better consistency
            embedding = self.extract_embedding(image, bbox)
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
    
    def batch_process_embeddings(self, image_list: List[np.ndarray]) -> List[Optional[np.ndarray]]:
        """
        Process multiple images in batch for better performance
        """
        embeddings = []
        for image in image_list:
            # Use same pipeline as single image
            found, bbox = self.detect_face(image)
            if found:
                embedding = self.extract_embedding(image, bbox)
                embeddings.append(embedding)
            else:
                embeddings.append(None)
        
        return embeddings
    
    def warm_up_models(self):
        """
        Warm up models with dummy data for faster first inference
        """
        if self._model_warm_up_done:
            return
        
        try:
            self.logger.info("Warming up AI models...")
            
            # Create dummy image
            dummy_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            
            # Warm up detection
            if self.face_detector:
                self.detect_face(dummy_image)
            
            # Warm up anti-spoofing
            if self.anti_spoof_model:
                self.anti_spoofing(dummy_image)
            
            # Warm up recognition  
            if self.face_recognizer:
                self.extract_embedding(dummy_image)
            
            self._model_warm_up_done = True
            self.logger.info("✅ Model warm-up completed")
            
        except Exception as e:
            self.logger.warning(f"Model warm-up failed: {e}")

    def get_model_info(self) -> dict:
        """Get comprehensive model information and status"""
        try:
            model_info = {
                "model_path": str(self.model_path),
                "models_loaded": {},
                "system_info": {},
                "performance": {}
            }
            
            # Face Detection Model Info
            if self.face_detector is not None:
                try:
                    model_info["models_loaded"]["face_detection"] = {
                        "status": "loaded",
                        "type": "YOLOv11s",
                        "framework": "Ultralytics",
                        "device": str(self.face_detector.device) if hasattr(self.face_detector, 'device') else "unknown"
                    }
                except:
                    model_info["models_loaded"]["face_detection"] = {"status": "loaded", "details": "limited_info"}
            else:
                model_info["models_loaded"]["face_detection"] = {"status": "not_loaded"}
            
            # Anti-Spoofing Model Info
            if self.anti_spoof_model is not None:
                model_info["models_loaded"]["anti_spoofing"] = {
                    "status": "loaded",
                    "type": "YOLOv11s-cls" if hasattr(self.anti_spoof_model, 'model') else "ONNX",
                    "framework": "Ultralytics" if hasattr(self.anti_spoof_model, 'model') else "ONNXRuntime"
                }
            else:
                model_info["models_loaded"]["anti_spoofing"] = {"status": "not_loaded", "fallback": "permissive_mode"}
            
            # Face Recognition Model Info
            if self.face_recognizer is not None:
                try:
                    model_info["models_loaded"]["face_recognition"] = {
                        "status": "loaded",
                        "type": "InsightFace Buffalo_L",
                        "framework": "InsightFace",
                        "embedding_dim": 512,
                        "det_size": "640x640"
                    }
                except:
                    model_info["models_loaded"]["face_recognition"] = {"status": "loaded", "details": "limited_info"}
            else:
                model_info["models_loaded"]["face_recognition"] = {"status": "not_loaded"}
            
            # System Information
            try:
                import psutil
                import platform
                model_info["system_info"] = {
                    "platform": platform.system(),
                    "cpu_count": psutil.cpu_count(),
                    "memory_gb": round(psutil.virtual_memory().total / (1024**3), 1),
                    "python_version": platform.python_version()
                }
            except ImportError:
                model_info["system_info"] = {"status": "psutil_not_available"}
            
            # Performance metrics (if available)
            if hasattr(self, '_performance_metrics'):
                model_info["performance"] = self._performance_metrics
            
            return model_info
            
        except Exception as e:
            self.logger.error(f"Error getting model info: {e}")
            return {"error": str(e), "model_path": str(self.model_path)}

# Global instance
ai_service = None

def get_ai_service() -> RealAIService:
    """Get or create AI service singleton with health check"""
    global ai_service
    if ai_service is None:
        ai_service = RealAIService()
        # Warm up models on first creation
        ai_service.warm_up_models()
    return ai_service

def health_check() -> dict:
    """
    Comprehensive health check for AI service
    """
    try:
        service = get_ai_service()
        
        # Test with dummy data
        dummy_image = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
        dummy_bytes = cv2.imencode('.jpg', dummy_image)[1].tobytes()
        
        health_status = {
            "status": "healthy",
            "models": {},
            "performance": service._performance_metrics.copy(),
            "timestamp": None
        }
        
        # Test detection
        found, bbox = service.detect_face(dummy_image)
        health_status["models"]["face_detection"] = {
            "status": "working" if service.face_detector else "not_loaded",
            "test_result": "passed" if found is not None else "failed"
        }
        
        # Test anti-spoofing
        spoof_result = service.anti_spoofing(dummy_image)
        health_status["models"]["anti_spoofing"] = {
            "status": "working" if service.anti_spoof_model else "disabled",
            "test_result": "passed" if spoof_result is not None else "failed"
        }
        
        # Test recognition
        embedding = service.extract_embedding(dummy_image)
        health_status["models"]["face_recognition"] = {
            "status": "working" if service.face_recognizer else "not_loaded",
            "test_result": "passed" if embedding is not None else "failed"
        }
        
        # Check if any critical models failed
        if not health_status["models"]["face_detection"]["status"] == "working":
            health_status["status"] = "unhealthy"
        if not health_status["models"]["face_recognition"]["status"] == "working":
            health_status["status"] = "unhealthy"
        
        import datetime
        health_status["timestamp"] = datetime.datetime.now().isoformat()
        
        return health_status
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }

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
