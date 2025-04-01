from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate

from .models import User
from .serializers import UserSerializer, LoginSerializer
from rest_framework_simplejwt.views import TokenRefreshView
# 用户注册
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # 允许所有用户访问（注册无需认证）

# 用户登录
class LoginView(APIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]  # 允许所有用户访问

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)  # 验证输入数据

        username = serializer.validated_data["username"].strip()  # 处理大小写和空格
        password = serializer.validated_data["password"]
        
        # 先检查用户是否存在
        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # 再验证密码
        user = authenticate(username=user.username, password=password)
        if not user:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)

        # 生成 JWT 令牌
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }, status=status.HTTP_200_OK)

class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom token refresh view that extends the default TokenRefreshView
    """
    def post(self, request, *args, **kwargs):
        # 使用父类的实现来刷新令牌
        response = super().post(request, *args, **kwargs)
        
        # 记录令牌刷新操作（可选）
        # 如果需要，可以在这里添加日志记录
        
        return response
