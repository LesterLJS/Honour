class ImageProcessingError(Exception):
    """Base exception for image processing errors."""
    
    def __init__(self, message="Image processing failed"):
        self.message = message
        super().__init__(self.message)

class BlockchainError(Exception):
    """Exception raised for blockchain interaction errors."""
    
    def __init__(self, message="Blockchain interaction failed"):
        self.message = message
        super().__init__(self.message)


class FeatureExtractionError(ImageProcessingError):
    """Exception raised when feature extraction fails."""
    
    def __init__(self, message="Feature extraction failed"):
        self.message = message
        super().__init__(self.message)

class FileValidationError(ImageProcessingError):
    """Exception raised when file validation fails."""
    
    def __init__(self, message="File validation failed"):
        self.message = message
        super().__init__(self.message)

class HashingError(ImageProcessingError):
    """Exception raised when hash calculation fails."""
    
    def __init__(self, message="Hash calculation failed"):
        self.message = message
        super().__init__(self.message)

class ModelError(ImageProcessingError):
    """Exception raised when model initialization or prediction fails."""
    
    def __init__(self, message="Model error"):
        self.message = message
        super().__init__(self.message)

class DeepfakeDetectionError(ImageProcessingError):
    """Exception raised when deepfake detection fails."""
    
    def __init__(self, message="Deepfake detection failed"):
        self.message = message
        super().__init__(self.message)

class SimilarImageError(Exception):
    """Exception raised when a similar image is found during verification."""
    
    def __init__(self, message="Similar image found", image_id=None, duplicate_type="similar", similarity=0.0, stage="unknown"):
        self.message = message
        self.image_id = image_id
        self.duplicate_type = duplicate_type  # "exact" or "similar"
        self.similarity = similarity  # Similarity score (0.0 to 1.0)
        self.stage = stage  # Which stage detected the similarity: "sha256", "orb", or "sift"
        super().__init__(self.message)
