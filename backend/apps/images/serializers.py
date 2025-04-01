from rest_framework import serializers
from .models import Image

class ImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    uploader_username = serializers.SerializerMethodField()
    
    class Meta:
        model = Image
        fields = [
            'id', 'sha256_hash', 'image_url', 'blockchain_tx',
            'deepfake_label', 'deepfake_confidence', 'is_verified',
            'uploader', 'uploader_username', 'uploaded_at'
        ]
    
    def get_image_url(self, obj):
        if obj.image_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_file.url)
            return obj.image_file.url
        return None
    
    def get_uploader_username(self, obj):
        return obj.uploader.username if obj.uploader else None