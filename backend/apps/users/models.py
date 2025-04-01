# apps/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Django 默认有 username, password, email 等字段
    # 新增一个 role 字段，区分管理员/普通用户
    role = models.CharField(max_length=20, default="user")  # 或 "admin"
    
    def __str__(self):
        return f"{self.username} ({self.role})"


