import logging
import threading
import os
import io
from django.core.files.base import ContentFile

from django.http import HttpResponse, JsonResponse, FileResponse
from django.conf import settings

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission

from .models import Image, AuditLog
from .serializers import ImageSerializer
from .services.detection_service import get_orb_features, get_sha256, deepfake_check, verify_image_similarity
from .services.exceptions import SimilarImageError

from .services.blockchain_service import store_image_on_blockchain

# Set up logging
logger = logging.getLogger(__name__)

class UploadImageView(APIView):
    """Upload image with IPFS storage"""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get("file", None)
        if not file_obj:
            return Response({"error": "请上传图片文件"}, status=status.HTTP_400_BAD_REQUEST)

        # Read file binary
        file_bytes = file_obj.read()
        sha256_hash = get_sha256(file_bytes)

        # 1. Check if exact same image exists using SHA256
        if Image.objects.filter(sha256_hash=sha256_hash).exists():
            return Response({
                "error": "Image Exist", 
                "stage": "sha256",
                "duplicate_type": "exact",
                "similarity": 1.0,
            }, status=status.HTTP_400_BAD_REQUEST)

        # 2. Perform progressive similarity verification (ORB -> SIFT)
        try:
            verify_image_similarity(file_bytes)
        except SimilarImageError as e:
            return Response({
                "error": e.message,
                "image_id": e.image_id,
                "stage": e.stage,
                "duplicate_type": e.duplicate_type,
                "similarity": e.similarity
            }, status=status.HTTP_400_BAD_REQUEST)

        # 3. Calculate SIFT and ORB features
        orb_features = get_orb_features(file_bytes)
  
        deepfake_result = deepfake_check(file_bytes)
    
        # Use a queue system for processing uploads to prevent resource contention
        # First, prepare all the data we need
        upload_data = {
            "sha256_hash": sha256_hash,
            "orb_features": orb_features,

            "deepfake_label": deepfake_result["label"],
            "deepfake_confidence": deepfake_result["confidence"],
            "uploader": request.user
        }
        
        blockchain_tx = None
        
        try:
            blockchain_tx = store_image_on_blockchain(
                sha256_hash, 
                deepfake_result["label"],
                deepfake_result["confidence"],
            )
        except Exception as e:
            logger.error(f"Failed to store on blockchain: {str(e)}")
            blockchain_tx = None

        # Handle the case where the image already exists on the blockchain
        if blockchain_tx == "IMAGE_EXISTS":
            logger.info(f"Image with hash {sha256_hash} already exists on blockchain. Creating database entry anyway.")
            blockchain_tx = "IMAGE_EXISTS"  # Keep the special value for reference

        # Store to database
        img = Image.objects.create(
            sha256_hash=sha256_hash,
            orb_features=orb_features,

            blockchain_tx=blockchain_tx,
            deepfake_label=deepfake_result["label"],
            deepfake_confidence=deepfake_result["confidence"],
            uploader=request.user
        )

        # 将图片文件保存到FileField
        # 从原始文件获取文件扩展名
        file_name = file_obj.name
        ext = file_name.split('.')[-1] if '.' in file_name else 'jpg'
        img.image_file.save(f"{sha256_hash}.{ext}", ContentFile(file_bytes), save=False)
        
        # 保存图片实例
        img.save()

        # Record upload log
        AuditLog.objects.create(
            user=request.user,
            action="upload",
            image=img,
            detail=f"User {request.user.username} uploaded image with hash={img.sha256_hash}"
        )

        serializer = ImageSerializer(img)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ImageFileView(APIView):
    """通过ID获取图片文件"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk, *args, **kwargs):
        logger.info(f"Request to access image with ID: {pk} by user: {request.user.username}")  # Log the request
        try:
            img = Image.objects.get(pk=pk)
            if img.image_file:
                return FileResponse(img.image_file.open(), content_type='image/jpeg')
            else:
                return Response({"error": "图片文件未找到"}, status=status.HTTP_404_NOT_FOUND)
        except Image.DoesNotExist:
            return Response({"error": "图片未找到"}, status=status.HTTP_404_NOT_FOUND)

class IsAdminUserCustom(BasePermission):
    """Custom admin permission"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)

class AdminDeleteImageView(APIView):
    """Admin delete image"""
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def delete(self, request, pk, *args, **kwargs):
        try:
            img = Image.objects.get(pk=pk)
            # Delete the image
            img.delete()
            return Response({"message": "Image Delete"})
        except Image.DoesNotExist:
            return Response({"error": "Image does not exist"}, status=status.HTTP_404_NOT_FOUND)

class AdminImagesView(APIView):
    """Admin get all images"""
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def get(self, request, *args, **kwargs):
        # Fetch all images with optional filtering and searching
        filters = {}
        if 'uploaded_by' in request.query_params:
            filters['uploader__username'] = request.query_params['uploaded_by']
        if 'deepfake_label' in request.query_params:
            filters['deepfake_label'] = request.query_params['deepfake_label']
        if 'is_verified' in request.query_params:
            filters['is_verified'] = request.query_params['is_verified'] == 'true'
        
        images = Image.objects.filter(**filters).order_by('-uploaded_at')
        
        # Implement pagination
        page = request.query_params.get('page', 1)
        limit = request.query_params.get('limit', 10)
        start = (int(page) - 1) * int(limit)
        end = start + int(limit)
        paginated_images = images[start:end]
        
        serializer = ImageSerializer(paginated_images, many=True)
        
        # Record access log
        AuditLog.objects.create(
            user=request.user,
            action="admin_list_images",
            detail=f"Admin {request.user.username} listed all images"
        )
        
        return Response({
            'total': images.count(),
            'images': serializer.data
        })

    def get_verified_images(self, request, *args, **kwargs):
        # Fetch only verified images
        verified_images = Image.objects.filter(is_verified=True).order_by('-uploaded_at')
        serializer = ImageSerializer(verified_images, many=True)
        
        return Response(serializer.data)
