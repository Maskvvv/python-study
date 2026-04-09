"""
Django 学习笔记 14 - 实战项目：个人博客系统
=====================================

亲爱的主人，让我们用 Django 创建一个完整的个人博客系统！💻
"""

# ============================================
# 项目概述
# ============================================
"""
功能模块：
    ✅ 文章管理（CRUD）
    ✅ 分类和标签
    ✅ 评论系统
    ✅ 用户认证
    ✅ 搜索功能
    ✅ 分页显示
    ✅ RSS 订阅
    ✅ 网站地图
"""

# ============================================
# 1. 项目结构
# ============================================
"""
blog_project/
├── manage.py
├── blog_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── blog/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── sitemaps.py
│   ├── feeds.py
│   ├── templatetags/
│   │   ├── __init__.py
│   │   └── blog_tags.py
│   ├── migrations/
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py
│       └── test_views.py
├── templates/
│   ├── base.html
│   └── blog/
│       ├── post_list.html
│       ├── post_detail.html
│       ├── post_form.html
│       └── ...
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── media/
├── requirements.txt
└── README.md
"""

# ============================================
# 2. 模型定义
# ============================================

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class Category(models.Model):
    """
    文章分类
    """
    name = models.CharField('分类名称', max_length=100)
    slug = models.SlugField('URL 别名', unique=True)
    description = models.TextField('分类描述', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog:category', args=[self.slug])
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    """
    文章标签
    """
    name = models.CharField('标签名称', max_length=50)
    slug = models.SlugField('URL 别名', unique=True)
    
    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog:tag', args=[self.slug])


class Post(models.Model):
    """
    文章模型
    """
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
    ]
    
    title = models.CharField('标题', max_length=200)
    slug = models.SlugField('URL 别名', unique_for_date='publish')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='作者'
    )
    content = models.TextField('内容')
    excerpt = models.TextField('摘要', blank=True)
    featured_image = models.ImageField(
        '特色图片',
        upload_to='posts/%Y/%m/%d/',
        blank=True,
        null=True
    )
    
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name='分类'
    )
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='标签')
    
    status = models.CharField(
        '状态',
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft'
    )
    publish = models.DateTimeField('发布时间', default=timezone.now)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    views = models.PositiveIntegerField('浏览次数', default=0)
    likes = models.PositiveIntegerField('点赞数', default=0)
    
    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[
            self.publish.year,
            self.publish.month,
            self.publish.day,
            self.slug
        ])
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.excerpt:
            self.excerpt = self.content[:200]
        super().save(*args, **kwargs)
    
    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])


class Comment(models.Model):
    """
    评论模型
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='文章'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='作者'
    )
    content = models.TextField('评论内容')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    active = models.BooleanField('是否显示', default=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name='父评论'
    )
    
    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['created_at']
    
    def __str__(self):
        return f'{self.author} 对 {self.post} 的评论'


# ============================================
# 3. 视图函数
# ============================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post, Category, Tag, Comment
from .forms import PostForm, CommentForm


class PostListView(ListView):
    """
    文章列表视图
    """
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Post.objects.filter(status='published')
        
        # 分类过滤
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # 标签过滤
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        # 搜索
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        context['popular_posts'] = Post.objects.filter(
            status='published'
        ).order_by('-views')[:5]
        return context


class PostDetailView(DetailView):
    """
    文章详情视图
    """
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    
    def get_object(self):
        obj = super().get_object()
        obj.increase_views()
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(active=True)
        context['comment_form'] = CommentForm()
        context['related_posts'] = Post.objects.filter(
            status='published',
            category=self.object.category
        ).exclude(id=self.object.id)[:3]
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """
    创建文章视图
    """
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, '文章创建成功！')
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    更新文章视图
    """
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, '文章更新成功！')
        return super().form_valid(form)
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_superuser


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    删除文章视图
    """
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = '/'
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_superuser


@login_required
def add_comment(request, post_id):
    """
    添加评论
    """
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, '评论发表成功！')
    
    return redirect(post.get_absolute_url())


# ============================================
# 4. URL 配置
# ============================================
"""
# blog/urls.py

from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # 文章列表
    path('', views.PostListView.as_view(), name='post_list'),
    
    # 文章详情
    path('post/<int:year>/<int:month>/<int:day>/<slug:slug>/',
         views.PostDetailView.as_view(),
         name='post_detail'),
    
    # 创建文章
    path('post/new/', views.PostCreateView.as_view(), name='post_create'),
    
    # 更新文章
    path('post/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post_update'),
    
    # 删除文章
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    
    # 添加评论
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    
    # 分类文章
    path('category/<slug:slug>/', views.category_posts, name='category'),
    
    # 标签文章
    path('tag/<slug:slug>/', views.tag_posts, name='tag'),
]
"""

# ============================================
# 5. RSS 订阅
# ============================================

from django.contrib.syndication.views import Feed
from django.urls import reverse


class LatestPostsFeed(Feed):
    """
    最新文章 RSS 订阅
    """
    title = "我的博客"
    link = "/"
    description = "最新发布的文章"
    
    def items(self):
        return Post.objects.filter(status='published')[:10]
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        return item.excerpt
    
    def item_link(self, item):
        return item.get_absolute_url()
    
    def item_author_name(self, item):
        return item.author.username
    
    def item_pubdate(self, item):
        return item.publish


# ============================================
# 6. 网站地图
# ============================================

from django.contrib.sitemaps import Sitemap


class PostSitemap(Sitemap):
    """
    文章网站地图
    """
    changefreq = 'weekly'
    priority = 0.9
    
    def items(self):
        return Post.objects.filter(status='published')
    
    def lastmod(self, obj):
        return obj.updated_at


class CategorySitemap(Sitemap):
    """
    分类网站地图
    """
    changefreq = 'monthly'
    priority = 0.7
    
    def items(self):
        return Category.objects.all()


# ============================================
# 7. requirements.txt
# ============================================
"""
Django==4.2.*
Pillow==10.*
django-ckeditor==6.*
django-taggit==4.*
django-contrib-comments==2.*
django-crispy-forms==2.*
crispy-bootstrap5==0.*
django-filter==23.*
django-debug-toolbar==4.*
gunicorn==21.*
whitenoise==6.*
django-redis==5.*
celery==5.*
django-celery-beat==2.*
sentry-sdk==1.*
"""

# ============================================
# 练习任务
# ============================================
"""
1. 完成博客系统的所有功能：
   - 文章 CRUD
   - 评论系统
   - 分类和标签
   - 搜索功能

2. 添加高级功能：
   - Markdown 编辑器
   - 代码高亮
   - 文章归档
   - 阅读进度条

3. 优化性能：
   - 数据库查询优化
   - 缓存热门文章
   - 静态文件压缩

4. 部署上线：
   - 配置生产环境
   - 设置 HTTPS
   - 配置域名

5. 编写测试：
   - 模型测试
   - 视图测试
   - API 测试
"""

if __name__ == "__main__":
    print("亲爱的主人，这是 Django 实战项目的学习笔记~ 🌸")
    print("请按照上面的步骤创建你的博客系统！")
    print("\n项目功能：")
    print("  ✅ 文章管理")
    print("  ✅ 分类标签")
    print("  ✅ 评论系统")
    print("  ✅ 搜索功能")
    print("  ✅ RSS 订阅")
    print("  ✅ 网站地图")
