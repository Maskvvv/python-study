"""
Django 学习笔记 09 - 静态文件和媒体文件
=====================================

亲爱的主人，让我们学习 Django 的静态文件和媒体文件管理！📁
"""

# ============================================
# 1. 静态文件概述
# ============================================
"""
静态文件：
    - CSS 样式表
    - JavaScript 脚本
    - 图片文件
    - 字体文件
    
媒体文件：
    - 用户上传的文件
    - 用户上传的图片
    - 其他用户生成的内容
"""

# ============================================
# 2. 静态文件配置
# ============================================
"""
# settings.py

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# 静态文件配置
STATIC_URL = '/static/'  # 静态文件 URL 前缀

# 静态文件目录（开发环境）
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# 静态文件收集目录（生产环境）
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 媒体文件配置
MEDIA_URL = '/media/'  # 媒体文件 URL 前缀
MEDIA_ROOT = BASE_DIR / 'media'  # 媒体文件存储目录

目录结构：
myproject/
├── static/              # 静态文件目录
│   ├── css/
│   │   ├── bootstrap.min.css
│   │   └── style.css
│   ├── js/
│   │   ├── bootstrap.bundle.min.js
│   │   └── main.js
│   ├── images/
│   │   ├── logo.png
│   │   └── avatar.jpg
│   └── fonts/
│       └── fontawesome/
├── media/               # 媒体文件目录
│   ├── avatars/
│   └── uploads/
└── staticfiles/         # 收集的静态文件（生产环境）
"""

# ============================================
# 3. 在模板中使用静态文件
# ============================================
"""
# 模板中使用静态文件

{% load static %}

<!DOCTYPE html>
<html>
<head>
    <!-- CSS 文件 -->
    <link rel="stylesheet" href="{% static 'css/bootstrap.min.css' %}">
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
    
    <!-- favicon -->
    <link rel="icon" href="{% static 'images/favicon.ico' %}">
</head>
<body>
    <!-- 图片 -->
    <img src="{% static 'images/logo.png' %}" alt="Logo">
    
    <!-- JavaScript 文件 -->
    <script src="{% static 'js/jquery.min.js' %}"></script>
    <script src="{% static 'js/bootstrap.bundle.min.js' %}"></script>
    <script src="{% static 'js/main.js' %}"></script>
</body>
</html>

# CSS 中使用静态文件（需要配置）

/* style.css */
.logo {
    background-image: url('../images/logo.png');
}
"""

# ============================================
# 4. 在视图中处理媒体文件
# ============================================

from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.core.files.storage import default_storage
from .models import Post
from .forms import PostForm


def upload_file(request):
    """
    文件上传视图
    """
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        
        # 保存文件
        file_path = default_storage.save(
            f'uploads/{uploaded_file.name}',
            uploaded_file
        )
        
        # 获取文件 URL
        file_url = default_storage.url(file_path)
        
        messages.success(request, f'文件上传成功！{file_url}')
        return redirect('upload')
    
    return render(request, 'blog/upload.html')


def create_post_with_image(request):
    """
    创建带图片的文章
    """
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            
            messages.success(request, '文章创建成功！')
            return redirect(post.get_absolute_url())
    else:
        form = PostForm()
    
    return render(request, 'blog/post_form.html', {'form': form})


# ============================================
# 5. 模型中的文件字段
# ============================================

from django.db import models


def user_avatar_path(instance, filename):
    """
    用户头像上传路径
    """
    return f'avatars/{instance.user.id}/{filename}'


def post_image_path(instance, filename):
    """
    文章图片上传路径
    """
    return f'posts/{instance.id}/{filename}'


class Profile(models.Model):
    """
    用户资料模型
    """
    user = models.OneToOneField(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='profile'
    )
    avatar = models.ImageField(
        '头像',
        upload_to=user_avatar_path,
        blank=True,
        null=True
    )
    resume = models.FileField(
        '简历',
        upload_to='resumes/',
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'
    
    def __str__(self):
        return f'{self.user.username} 的资料'


class Post(models.Model):
    """
    文章模型
    """
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    featured_image = models.ImageField(
        '特色图片',
        upload_to=post_image_path,
        blank=True,
        null=True
    )
    attachment = models.FileField(
        '附件',
        upload_to='attachments/',
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'


# ============================================
# 6. 文件上传表单
# ============================================

from django import forms


class AvatarUploadForm(forms.Form):
    """
    头像上传表单
    """
    avatar = forms.ImageField(
        label='选择头像',
        help_text='支持 JPG、PNG 格式，最大 2MB'
    )
    
    def clean_avatar(self):
        avatar = self.cleaned_data['avatar']
        
        # 检查文件大小
        if avatar.size > 2 * 1024 * 1024:
            raise forms.ValidationError('文件大小不能超过 2MB')
        
        # 检查文件类型
        if avatar.content_type not in ['image/jpeg', 'image/png']:
            raise forms.ValidationError('只支持 JPG 和 PNG 格式')
        
        return avatar


class MultipleFileInput(forms.ClearableFileInput):
    """
    多文件上传控件
    """
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """
    多文件上传字段
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)
    
    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class GalleryForm(forms.Form):
    """
    图库上传表单
    """
    images = MultipleFileField(
        label='选择图片',
        help_text='可以一次选择多张图片'
    )


# ============================================
# 7. 多文件上传视图
# ============================================

def upload_gallery(request):
    """
    多文件上传
    """
    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES)
        if form.is_valid():
            images = request.FILES.getlist('images')
            
            for image in images:
                GalleryImage.objects.create(
                    image=image,
                    user=request.user
                )
            
            messages.success(request, f'成功上传 {len(images)} 张图片！')
            return redirect('gallery')
    else:
        form = GalleryForm()
    
    return render(request, 'blog/gallery_upload.html', {'form': form})


# ============================================
# 8. 图片处理
# ============================================

from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import os


def resize_image(image, max_width=800, max_height=600):
    """
    调整图片大小
    """
    img = Image.open(image)
    
    # 获取原始尺寸
    width, height = img.size
    
    # 计算新尺寸
    if width > max_width or height > max_height:
        ratio = min(max_width / width, max_height / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        # 调整大小
        img = img.resize((new_width, new_height), Image.LANCZOS)
    
    # 保存到内存
    output = BytesIO()
    img_format = image.name.split('.')[-1].upper()
    if img_format == 'JPG':
        img_format = 'JPEG'
    
    img.save(output, format=img_format, quality=85)
    output.seek(0)
    
    # 创建新的文件对象
    return InMemoryUploadedFile(
        output,
        'ImageField',
        image.name,
        f'image/{img_format.lower()}',
        output.getbuffer().nbytes,
        None
    )


def create_thumbnail(image, size=(200, 200)):
    """
    创建缩略图
    """
    img = Image.open(image)
    img.thumbnail(size, Image.LANCZOS)
    
    # 保存缩略图
    thumb_name = f'thumb_{image.name}'
    thumb_path = os.path.join(settings.MEDIA_ROOT, 'thumbnails', thumb_name)
    
    os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
    img.save(thumb_path)
    
    return f'thumbnails/{thumb_name}'


# ============================================
# 9. 开发环境配置
# ============================================
"""
# urls.py（开发环境）

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
]

# 开发环境下提供静态文件和媒体文件服务
if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
"""

# ============================================
# 10. 生产环境配置
# ============================================
"""
# settings.py（生产环境）

DEBUG = False

# 使用 WhiteNoise 提供静态文件
# pip install whitenoise

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # 添加这行
    ...
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 使用云存储（如 AWS S3）
# pip install django-storages boto3

INSTALLED_APPS = [
    ...
    'storages',
]

AWS_ACCESS_KEY_ID = 'your-access-key'
AWS_SECRET_ACCESS_KEY = 'your-secret-key'
AWS_STORAGE_BUCKET_NAME = 'your-bucket-name'
AWS_S3_REGION_NAME = 'ap-northeast-1'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'

AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
"""

# ============================================
# 11. 静态文件收集命令
# ============================================
"""
# 收集所有静态文件到 STATIC_ROOT
python manage.py collectstatic

# 清除已收集的静态文件
python manage.py collectstatic --clear

# 不需要确认直接收集
python manage.py collectstatic --noinput

# 查看将要收集的文件
python manage.py collectstatic --dry-run
"""

# ============================================
# 12. 文件存储后端
# ============================================

from django.core.files.storage import FileSystemStorage
from django.conf import settings


class CustomStorage(FileSystemStorage):
    """
    自定义文件存储
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('location', settings.MEDIA_ROOT)
        kwargs.setdefault('base_url', settings.MEDIA_URL)
        super().__init__(*args, **kwargs)
    
    def get_available_name(self, name, max_length=None):
        """
        文件名冲突时添加序号
        """
        if self.exists(name):
            base, ext = os.path.splitext(name)
            counter = 1
            while self.exists(f'{base}_{counter}{ext}'):
                counter += 1
            name = f'{base}_{counter}{ext}'
        return name
    
    def _save(self, name, content):
        """
        保存文件时添加处理
        """
        # 可以在这里添加文件处理逻辑
        return super()._save(name, content)


# ============================================
# 13. 模板示例
# ============================================
"""
# templates/blog/upload.html

{% extends 'base.html' %}
{% load static %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <h2>📁 文件上传</h2>
        
        <form method="post" enctype="multipart/form-data">
            {% csrf_token %}
            
            <div class="mb-3">
                <label for="file" class="form-label">选择文件</label>
                <input type="file" class="form-control" id="file" name="file">
            </div>
            
            <button type="submit" class="btn btn-primary">上传</button>
        </form>
        
        {% if user.profile.avatar %}
        <div class="mt-4">
            <h5>当前头像</h5>
            <img src="{{ user.profile.avatar.url }}" 
                 alt="头像" 
                 class="img-thumbnail"
                 style="max-width: 200px;">
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}

# 显示媒体文件

<img src="{{ post.featured_image.url }}" alt="{{ post.title }}">
<a href="{{ post.attachment.url }}">下载附件</a>
"""

# ============================================
# 练习任务
# ============================================
"""
1. 配置静态文件和媒体文件目录

2. 创建文件上传功能：
   - 单文件上传
   - 多文件上传
   - 图片上传

3. 实现图片处理：
   - 调整大小
   - 创建缩略图
   - 压缩图片

4. 配置生产环境的静态文件服务

5. 使用云存储（如 AWS S3）
"""

if __name__ == "__main__":
    print("亲爱的主人，这是 Django 静态文件和媒体文件的学习笔记~ 🌸")
    print("请按照上面的步骤学习文件管理！")
    print("\n关键命令：")
    print("  python manage.py collectstatic")
    print("\n关键配置：")
    print("  STATIC_URL = '/static/'")
    print("  MEDIA_URL = '/media/'")
