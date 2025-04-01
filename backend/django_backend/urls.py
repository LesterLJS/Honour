# django_backend/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def home_view(request):
    return JsonResponse({"message": "Welcome to My Django Backend!"})

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.users.urls")),
    path("api/images/", include("apps.images.urls")),
    path('', home_view),  # 添加根路径
    # 其它...
]

