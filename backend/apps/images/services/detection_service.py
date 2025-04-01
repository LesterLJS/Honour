import hashlib
import io
import logging
import numpy as np
import cv2
import time
from PIL import Image as PILImage
from scipy.fftpack import dct

import tensorflow as tf
from django.conf import settings
from django.db.models import Q
from apps.images.models import Image
from apps.images.services.exceptions import SimilarImageError, FeatureExtractionError

# Set up logging
logger = logging.getLogger(__name__)

# Configure logging format if not already configured
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Load the deepfake detection model
try:
    deepfake_model = tf.keras.models.load_model(
        settings.BASE_DIR / 'apps' / 'images' / 'models' / 'xception_deepfake.h5'
    )
    logger.info("Deepfake detection model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load deepfake detection model: {str(e)}")
    deepfake_model = None


def get_sha256(file_bytes):
    """
    Calculate SHA256 hash of file bytes.
    
    Args:
        file_bytes: Bytes of the file
        
    Returns:
        str: SHA256 hash as hexadecimal string
    """
    logger.info("Starting SHA256 hash calculation")
    start_time = time.time()
    
    try:
        hash_result = hashlib.sha256(file_bytes).hexdigest()
        elapsed_time = time.time() - start_time
        logger.info(f"SHA256 hash calculation completed in {elapsed_time:.3f}s: {hash_result[:10]}...")
        return hash_result
    except Exception as e:
        logger.error(f"Error calculating SHA256 hash: {str(e)}")
        raise

def get_orb_features(file_bytes):
    """
    Extract ORB features from an image.
    
    Args:
        file_bytes: Bytes of the image file
        
    Returns:
        dict: Dictionary containing keypoints and descriptors
    """
    logger.info("Starting ORB feature extraction")
    start_time = time.time()
    
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            logger.error("Failed to decode image for ORB feature extraction")
            raise FeatureExtractionError("Failed to decode image")
        
        logger.debug(f"Image decoded successfully: shape={img.shape}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Initialize ORB detector
        orb = cv2.ORB_create(nfeatures=1000)
        logger.debug("ORB detector initialized with nfeatures=1000")
        
        # Detect keypoints and compute descriptors
        keypoints, descriptors = orb.detectAndCompute(gray, None)
        
        if keypoints is None or len(keypoints) == 0 or descriptors is None:
            logger.warning("No ORB features detected in image")
            return None
        
        logger.debug(f"Detected {len(keypoints)} ORB keypoints")
        
        # Convert keypoints to serializable format
        keypoints_list = []
        for kp in keypoints:
            keypoints_list.append({
                'pt': (float(kp.pt[0]), float(kp.pt[1])),
                'size': float(kp.size),
                'angle': float(kp.angle),
                'response': float(kp.response),
                'octave': int(kp.octave),
                'class_id': int(kp.class_id) if kp.class_id is not None else -1
            })
        
        # Convert descriptors to serializable format
        descriptors_list = descriptors.tolist() if descriptors is not None else []
        
        elapsed_time = time.time() - start_time
        logger.info(f"ORB feature extraction completed in {elapsed_time:.3f}s: {len(keypoints)} keypoints extracted")
        
        return {
            'keypoints': keypoints_list,
            'descriptors': descriptors_list
        }
    except Exception as e:
        logger.error(f"Error extracting ORB features: {str(e)}")
        raise FeatureExtractionError(f"Failed to extract ORB features: {str(e)}")

def compare_orb_features(features1, features2):
    """
    Compare two sets of ORB features and return similarity score.
    
    Args:
        features1: First set of ORB features
        features2: Second set of ORB features
        
    Returns:
        float: Similarity score between 0 and 1 (1 being identical)
    """
    logger.info("Starting ORB feature comparison")
    start_time = time.time()
    
    try:
        # Convert string to dict if needed
        if isinstance(features1, str):
            try:
                import json
                features1 = json.loads(features1)
                logger.info("Successfully converted features1 from string to dict")
            except Exception as e:
                logger.error(f"Failed to convert features1 from string to dict: {str(e)}")
                return 0.0
                
        if isinstance(features2, str):
            try:
                import json
                features2 = json.loads(features2)
                logger.info("Successfully converted features2 from string to dict")
            except Exception as e:
                logger.error(f"Failed to convert features2 from string to dict: {str(e)}")
                return 0.0
        
        # Validate input features
        if not isinstance(features1, dict) or not isinstance(features2, dict):
            logger.error(f"Invalid feature type after conversion: features1={type(features1)}, features2={type(features2)}")
            return 0.0
            
        # Check if features are valid
        if not features1 or not features2:
            logger.warning("Invalid ORB features: one or both feature sets are empty")
            return 0.0
        
        if 'descriptors' not in features1 or 'descriptors' not in features2:
            logger.warning("Invalid ORB features: missing descriptors")
            return 0.0
            
        # Log feature structure for debugging
        logger.debug(f"Features1 keys: {features1.keys()}")
        logger.debug(f"Features2 keys: {features2.keys()}")
        logger.debug(f"Descriptors1 type: {type(features1['descriptors'])}")
        logger.debug(f"Descriptors2 type: {type(features2['descriptors'])}")
        
        # Deep copy to avoid modifying original data
        import copy
        features1_copy = copy.deepcopy(features1)
        features2_copy = copy.deepcopy(features2)
        
        # Handle potential string/JSON serialization of descriptors
        try:
            if isinstance(features1_copy['descriptors'], str):
                import json
                features1_copy['descriptors'] = json.loads(features1_copy['descriptors'])
                logger.debug("Successfully deserialized descriptors1 from JSON")
            if isinstance(features2_copy['descriptors'], str):
                import json
                features2_copy['descriptors'] = json.loads(features2_copy['descriptors'])
                logger.debug("Successfully deserialized descriptors2 from JSON")
        except Exception as e:
            logger.error(f"Error deserializing descriptors: {str(e)}")
            return 0.0
            
        # Ensure descriptors are lists before converting to numpy arrays
        if not isinstance(features1_copy['descriptors'], list) or not isinstance(features2_copy['descriptors'], list):
            logger.error(f"Invalid descriptor types after deserialization: descriptors1={type(features1_copy['descriptors'])}, descriptors2={type(features2_copy['descriptors'])}")
            return 0.0
            
        # Validate descriptor contents
        if any(not isinstance(d, list) for d in features1_copy['descriptors']) or \
           any(not isinstance(d, list) for d in features2_copy['descriptors']):
            logger.error("Invalid descriptor format: descriptors must be list of lists")
            return 0.0
            
        try:
            descriptors1 = np.array(features1_copy['descriptors'], dtype=np.uint8)
            descriptors2 = np.array(features2_copy['descriptors'], dtype=np.uint8)
            logger.debug(f"Successfully converted descriptors to numpy arrays: shapes={descriptors1.shape}, {descriptors2.shape}")
        except Exception as e:
            logger.error(f"Error converting descriptors to numpy arrays: {str(e)}")
            return 0.0
        
        if len(descriptors1) == 0 or len(descriptors2) == 0:
            logger.warning("Empty descriptors in ORB features")
            return 0.0
        
        logger.debug(f"Comparing ORB features: {len(descriptors1)} vs {len(descriptors2)} descriptors")
        
        # Create BFMatcher object
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        
        # Match descriptors
        matches = bf.match(descriptors1, descriptors2)
        
        # Sort them in order of distance
        matches = sorted(matches, key=lambda x: x.distance)
        
        # Calculate similarity score based on number of good matches
        # and their average distance
        if len(matches) == 0:
            logger.warning("No matches found between ORB features")
            return 0.0
        
        # Use only good matches (lower distance is better)
        good_matches = [m for m in matches if m.distance < 50]
        logger.debug(f"Found {len(good_matches)} good matches out of {len(matches)} total matches")
        
        # Calculate similarity based on number of good matches relative to total features
        max_possible_matches = min(len(descriptors1), len(descriptors2))
        similarity = len(good_matches) / max_possible_matches if max_possible_matches > 0 else 0.0
        
        elapsed_time = time.time() - start_time
        logger.info(f"ORB comparison completed in {elapsed_time:.3f}s: similarity={similarity:.4f}")
        
        return min(1.0, similarity)  # Cap at 1.0
    except Exception as e:
        logger.error(f"Error comparing ORB features: {str(e)}")
        return 0.0

def verify_image_similarity(file_bytes):
    """
    Verify if an image is similar to any existing image using SHA256 hash and ORB features.
    The function only uses ORB features without SIFT verification.
    
    Args:
        file_bytes: Bytes of the image file
        
    Returns:
        None if no similar image is found
        
    Raises:
        SimilarImageError: If a similar image is found
    """
    logger.info("Starting image similarity verification")
    total_start_time = time.time()
    
    # Calculate SHA256 hash for exact duplicate check
    file_hash = get_sha256(file_bytes)
    logger.info(f"Image hash: {file_hash[:10]}...")
    
    # Check for exact duplicates by hash
    exact_match = Image.objects.filter(sha256_hash=file_hash).first()
    if exact_match:
        logger.warning(f"Exact duplicate image found: ID={exact_match.id}, Hash={file_hash[:10]}...")
        raise SimilarImageError(
            message="Exact duplicate image found",
            image_id=exact_match.id,
            duplicate_type="exact",
            similarity=1.0,
            stage="sha256"
        )
    
    # Extract ORB features from the query image
    query_orb_features = get_orb_features(file_bytes)
    
    if not query_orb_features:
        logger.warning("Could not extract ORB features from query image")
        return None
    
    # Get all images with ORB features
    images = Image.objects.filter(orb_features__isnull=False)
    logger.info(f"Comparing against {images.count()} images with ORB features")
    
    # ORB similarity check
    orb_threshold = 0.6  # 60% similarity threshold for ORB - adjusted for more accuracy without SIFT second pass
    
    # Track all similarities for debugging
    all_similarities = []
    
    for img in images:
        try:
            # Skip images without ORB features
            if not img.orb_features:
                continue
            
            # Calculate ORB similarity
            orb_similarity = compare_orb_features(query_orb_features, img.orb_features)
            
            # Store all similarities for debugging
            all_similarities.append({
                'image_id': img.id,
                'similarity': orb_similarity
            })
            
            # If similarity is above threshold, consider it a similar image
            if orb_similarity >= orb_threshold:
                logger.warning(f"Similar image found: ID={img.id} with ORB similarity {orb_similarity:.4f}")
                
                total_elapsed_time = time.time() - total_start_time
                logger.info(f"Image similarity verification completed in {total_elapsed_time:.3f}s: Similar image found")
                
                raise SimilarImageError(
                    message=f"Similar image found with {orb_similarity:.2%} similarity",
                    image_id=img.id,
                    duplicate_type="similar",
                    similarity=orb_similarity,
                    stage="orb"
                )
        except SimilarImageError:
            # Re-raise the exception
            raise
        except Exception as e:
            logger.error(f"Error comparing ORB features for image {img.id}: {str(e)}")
    
    # Log top similarities for debugging
    all_similarities.sort(key=lambda x: x['similarity'], reverse=True)
    top_similarities = all_similarities[:10] if len(all_similarities) >= 10 else all_similarities
    logger.info(f"Top ORB similarities: {top_similarities}")
    
    # If no candidates pass the ORB threshold, return None
    total_elapsed_time = time.time() - total_start_time
    logger.info(f"Image similarity verification completed in {total_elapsed_time:.3f}s: No similar images found")
    return None

def deepfake_check(file_bytes):
    """
    Perform deepfake detection on an image.
    
    Args:
        file_bytes: Bytes of the image file
        
    Returns:
        dict: Dictionary with detection results
    """
    try:
        if deepfake_model is None:
            logger.warning("Deepfake detection model not loaded")
            return {"label": "Unknown", "confidence": 0.0}
        
        # Preprocess image for the model
        img = PILImage.open(io.BytesIO(file_bytes))
        img = img.resize((299, 299))  # Xception input size
        img = img.convert('RGB')
        
        # Convert to numpy array and normalize
        img_array = np.array(img)
        img_array = img_array.astype('float32') / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        # Make prediction
        prediction = deepfake_model.predict(img_array)[0][0]
        
        # Interpret prediction (assuming 0 = real, 1 = fake)
        # Adjust threshold as needed
        label = "Fake" if prediction > 0.5 else "Real"
        confidence = float(prediction) if label == "Fake" else 1.0 - float(prediction)
        
        return {
            "label": label,
            "confidence": confidence
        }
    except Exception as e:
        logger.error(f"Error in deepfake detection: {str(e)}")
        return {"label": "Unknown", "confidence": 0.0}
