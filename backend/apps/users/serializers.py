# apps/users/serializers.py
from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model

# Use the model directly for UserSerializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password", "role", "email"]
        extra_kwargs = {
            "password": {"write_only": True},
            "role": {"read_only": True}  # 防止用户在注册时设置角色
        }

    def create(self, validated_data):
        # 确保新用户的角色始终为"user"
        validated_data["role"] = "user"
        
        # Hash the password
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

# Use get_user_model for LoginSerializer
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
