# apps/images/models.py
from django.db import models
from django.conf import settings

def image_upload_path(instance, filename):
    # 生成类似 'images/sha256_hash.jpg' 的路径
    ext = filename.split('.')[-1]
    return f'images/{instance.sha256_hash}.{ext}'

class Image(models.Model):
    sha256_hash = models.CharField(max_length=64, unique=True)
 
    orb_features = models.JSONField(null=True, blank=True)  # ORB features in JSON format
    sift_features = models.JSONField(null=True, blank=True)  # SIFT features in JSON format
    
    blockchain_tx = models.CharField(max_length=255, null=True, blank=True)
    image_file = models.FileField(upload_to=image_upload_path, null=True, blank=True)
    # Deepfake results
    deepfake_label = models.CharField(max_length=10, null=True, blank=True)  # "Real" or "Fake"
    deepfake_confidence = models.FloatField(null=True, blank=True)
    
    # Verification status
    is_verified = models.BooleanField(default=False)
   
   

    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="images"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id} - {self.sha256_hash[:10]}"
    

class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="audit_logs"
    )
    action = models.CharField(max_length=50)
    image = models.ForeignKey(
        Image,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="audit_logs"
    )
    detail = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.timestamp}] user={self.user_id}, action={self.action}"