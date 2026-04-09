"""
Django 学习笔记 13 - Django REST Framework
=====================================

亲爱的主人，让我们学习 Django REST Framework 构建 API！🌐
"""

# ============================================
# 1. REST Framework 概述
# ============================================
"""
Django REST Framework (DRF) 是一个强大灵活的工具包，用于构建 Web API。

特点：
    ✅ 可浏览的 API
    ✅ 认证和权限
    ✅ 序列化
    ✅ 分页
    ✅ 过滤和搜索
    ✅ 版本控制
"""

# ============================================
# 2. 安装和配置
# ============================================
"""
# 安装
pip install djangorestframework
pip install markdown
pip install django-filter

# settings.py
INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework.authtoken',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}
"""

# ============================================
# 3. 序列化器（Serializer）
# ============================================

from rest_framework import serializers
from .models import Post, Category, Tag, Comment


class CategorySerializer(serializers.ModelSerializer):
    """
    分类序列化器
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']


class TagSerializer(serializers.ModelSerializer):
    """
    标签序列化器
    """
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class PostSerializer(serializers.ModelSerializer):
    """
    文章序列化器
    """
    author = serializers.ReadOnlyField(source='author.username')
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        source='tags',
        many=True,
        write_only=True
    )
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'author', 'content',
            'category', 'category_id', 'tags', 'tag_ids',
            'status', 'publish', 'views', 'likes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['views', 'likes', 'created_at', 'updated_at']
    
    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError('标题至少需要 5 个字符')
        return value
    
    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        post = Post.objects.create(**validated_data)
        post.tags.set(tags)
        return post
    
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if tags is not None:
            instance.tags.set(tags)
        
        return instance


class CommentSerializer(serializers.ModelSerializer):
    """
    评论序列化器
    """
    author = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at', 'active']
        read_only_fields = ['author', 'created_at']


# ============================================
# 4. 视图集（ViewSets）
# ============================================

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend


class PostViewSet(viewsets.ModelViewSet):
    """
    文章视图集
    提供完整的 CRUD 操作
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'category', 'tags']
    search_fields = ['title', 'content']
    ordering_fields = ['publish', 'views', 'likes']
    ordering = ['-publish']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(status='published')
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """点赞功能"""
        post = self.get_object()
        post.likes += 1
        post.save()
        return Response({'status': 'liked', 'likes': post.likes})
    
    @action(detail=False)
    def my_posts(self, request):
        """获取当前用户的文章"""
        posts = Post.objects.filter(author=request.user)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
    
    @action(detail=False)
    def popular(self, request):
        """获取热门文章"""
        posts = Post.objects.filter(
            status='published'
        ).order_by('-views')[:10]
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    分类视图集（只读）
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    标签视图集（只读）
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """
    评论视图集
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        post_id = self.request.query_params.get('post')
        
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# ============================================
# 5. API 视图（函数式）
# ============================================

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.urls import reverse


@api_view(['GET'])
def api_root(request):
    """
    API 根路径
    """
    return Response({
        'posts': reverse('post-list', request=request),
        'categories': reverse('category-list', request=request),
        'tags': reverse('tag-list', request=request),
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def post_list_create(request):
    """
    文章列表和创建
    """
    if request.method == 'GET':
        posts = Post.objects.filter(status='published')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def post_detail(request, pk):
    """
    文章详情、更新、删除
    """
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = PostSerializer(post)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================
# 6. 通用视图
# ============================================

from rest_framework import generics


class PostListAPIView(generics.ListCreateAPIView):
    """
    文章列表视图
    """
    queryset = Post.objects.filter(status='published')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    文章详情视图
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# ============================================
# 7. 认证和权限
# ============================================

from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
    TokenAuthentication,
)
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
)


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    自定义权限：只有作者可以编辑
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.author == request.user


class PostViewSetWithPermission(viewsets.ModelViewSet):
    """
    带权限的文章视图集
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    authentication_classes = [
        TokenAuthentication,
        SessionAuthentication,
    ]
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]


# ============================================
# 8. 分页
# ============================================
"""
# settings.py

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}
"""

from rest_framework.pagination import (
    PageNumberPagination,
    LimitOffsetPagination,
    CursorPagination,
)


class CustomPagination(PageNumberPagination):
    """
    自定义分页
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class PostViewSetWithPagination(viewsets.ModelViewSet):
    """
    带自定义分页的文章视图集
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = CustomPagination


# ============================================
# 9. 过滤和搜索
# ============================================

import django_filters


class PostFilter(django_filters.FilterSet):
    """
    文章过滤器
    """
    title = django_filters.CharFilter(lookup_expr='icontains')
    content = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.ChoiceFilter(choices=Post.STATUS_CHOICES)
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all())
    tags = django_filters.ModelMultipleChoiceFilter(queryset=Tag.objects.all())
    publish_after = django_filters.DateTimeFilter(field_name='publish', lookup_expr='gte')
    publish_before = django_filters.DateTimeFilter(field_name='publish', lookup_expr='lte')
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'status', 'category', 'tags']


class PostViewSetWithFilter(viewsets.ModelViewSet):
    """
    带过滤的文章视图集
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PostFilter


# ============================================
# 10. URL 配置
# ============================================
"""
# urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建路由器
router = DefaultRouter()
router.register('posts', views.PostViewSet)
router.register('categories', views.CategoryViewSet)
router.register('tags', views.TagViewSet)
router.register('comments', views.CommentViewSet)

urlpatterns = [
    # API 根路径
    path('', views.api_root),
    
    # 视图集路由
    path('api/', include(router.urls)),
    
    # 函数式视图
    path('posts/', views.post_list_create, name='post-list'),
    path('posts/<int:pk>/', views.post_detail, name='post-detail'),
    
    # 认证
    path('api-auth/', include('rest_framework.urls')),
]
"""

# ============================================
# 11. Token 认证
# ============================================
"""
# 生成 Token
from rest_framework.authtoken.models import Token

# 为用户创建 Token
token = Token.objects.create(user=user)
print(token.key)

# 在请求中使用 Token
# Header: Authorization: Token your-token-here

# urls.py
from rest_framework.authtoken import views

urlpatterns = [
    path('api-token-auth/', views.obtain_auth_token),
]
"""

# ============================================
# 12. JWT 认证
# ============================================
"""
# 安装
pip install djangorestframework-simplejwt

# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

# urls.py
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# 使用
# 1. POST /api/token/ 获取 access 和 refresh token
# 2. 使用 access token 访问 API
# 3. POST /api/token/refresh/ 刷新 token
"""

# ============================================
# 13. API 文档
# ============================================
"""
# 安装
pip install drf-yasg

# urls.py
from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Blog API",
        default_version='v1',
        description="博客 API 文档",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# 访问
# http://localhost:8000/swagger/
# http://localhost:8000/redoc/
"""

# ============================================
# 14. 限流（Throttling）
# ============================================
"""
# settings.py

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
    },
}

# 自定义限流
from rest_framework.throttling import UserRateThrottle

class BurstRateThrottle(UserRateThrottle):
    scope = 'burst'

class SustainedRateThrottle(UserRateThrottle):
    scope = 'sustained'

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'burst': '60/min',
        'sustained': '1000/day',
    },
}
"""

# ============================================
# 15. 版本控制
# ============================================
"""
# settings.py

REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'ALLOWED_VERSIONS': ['v1', 'v2'],
    'DEFAULT_VERSION': 'v1',
}

# urls.py
urlpatterns = [
    path('api/<str:version>/', include('blog.urls')),
]

# 视图中使用
def get_serializer_class(self):
    if self.request.version == 'v2':
        return PostSerializerV2
    return PostSerializer
"""

# ============================================
# 练习任务
# ============================================
"""
1. 创建序列化器：
   - CategorySerializer
   - PostSerializer
   - CommentSerializer

2. 创建视图集：
   - PostViewSet（CRUD）
   - CommentViewSet

3. 配置认证：
   - Token 认证
   - JWT 认证

4. 配置权限：
   - IsAuthenticated
   - IsAuthorOrReadOnly

5. 配置分页、过滤、搜索

6. 生成 API 文档
"""

if __name__ == "__main__":
    print("亲爱的主人，这是 Django REST Framework 的学习笔记~ 🌸")
    print("请按照上面的步骤学习 DRF！")
    print("\n关键概念：")
    print("  - Serializer：序列化器")
    print("  - ViewSet：视图集")
    print("  - Authentication：认证")
    print("  - Permission：权限")
    print("  - Pagination：分页")
