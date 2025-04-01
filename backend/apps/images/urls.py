from django.urls import path
from .views import UploadImageView, AdminImagesView, AdminDeleteImageView, ImageFileView

urlpatterns = [
    path('upload/', UploadImageView.as_view(), name='upload_image'),
    path('admin/images/', AdminImagesView.as_view(), name='admin_images'),
    path('admin/images/verified/', AdminImagesView.as_view(), name='admin_verified_images'),  # Corrected
    path('admin/images/<int:pk>/', AdminDeleteImageView.as_view(), name='admin_delete_image'),
    path('<int:pk>/file/', ImageFileView.as_view(), name='image_file'),
]