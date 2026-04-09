"""
Django 学习笔记 06 - 用户认证系统
=====================================

亲爱的主人，让我们学习 Django 强大的用户认证系统！🔐
"""

# ============================================
# 1. Django 认证系统概述
# ============================================
"""
Django 内置的认证系统提供：
    ✅ 用户模型（User）
    ✅ 权限和组
    ✅ 认证视图（登录、登出、密码重置等）
    ✅ 认证装饰器
    ✅ 密码哈希
"""

# ============================================
# 2. 用户模型
# ============================================

from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


def user_operations():
    """
    用户基本操作
    """
    # 创建用户
    user = User.objects.create_user(
        username='xiaoming',
        email='xiaoming@example.com',
        password='password123',
        first_name='小明',
        last_name='王'
    )
    
    # 创建超级用户
    superuser = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
    
    # 获取用户
    user = User.objects.get(username='xiaoming')
    
    # 修改用户信息
    user.first_name = '小明'
    user.email = 'newemail@example.com'
    user.save()
    
    # 修改密码
    user.set_password('newpassword123')
    user.save()
    
    # 检查密码
    if user.check_password('newpassword123'):
        print('密码正确')
    
    # 删除用户
    user.delete()


# ============================================
# 3. 自定义用户模型
# ============================================

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    自定义用户模型
    """
    avatar = models.ImageField(
        '头像',
        upload_to='avatars/',
        blank=True,
        null=True
    )
    phone = models.CharField(
        '手机号',
        max_length=11,
        blank=True
    )
    bio = models.TextField(
        '个人简介',
        max_length=500,
        blank=True
    )
    website = models.URLField(
        '个人网站',
        blank=True
    )
    birthday = models.DateField(
        '生日',
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
    
    def __str__(self):
        return self.username
    
    def get_full_name_cn(self):
        """获取中文全名"""
        return f'{self.last_name}{self.first_name}'


# settings.py 中配置：
# AUTH_USER_MODEL = 'blog.CustomUser'


# ============================================
# 4. 认证视图
# ============================================

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy


def login_view(request):
    """
    登录视图
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            if not remember:
                request.session.set_expiry(0)
            
            messages.success(request, f'欢迎回来，{user.username}！🌸')
            
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, '用户名或密码错误')
    
    return render(request, 'registration/login.html')


def logout_view(request):
    """
    登出视图
    """
    logout(request)
    messages.success(request, '已成功退出登录')
    return redirect('home')


class SignUpView(CreateView):
    """
    注册视图
    """
    model = CustomUser
    template_name = 'registration/signup.html'
    fields = ['username', 'email', 'password1', 'password2']
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, '注册成功！请登录')
        return response


# ============================================
# 5. 认证装饰器
# ============================================

@login_required
def profile(request):
    """
    用户个人资料页面（需要登录）
    """
    return render(request, 'blog/profile.html', {'user': request.user})


@login_required(login_url='/login/')
def settings(request):
    """
    用户设置页面（自定义登录 URL）
    """
    return render(request, 'blog/settings.html')


@permission_required('blog.add_post', raise_exception=True)
def create_post(request):
    """
    创建文章（需要权限）
    """
    pass


def custom_permission_check(request):
    """
    手动检查权限
    """
    if request.user.has_perm('blog.change_post'):
        pass
    
    if request.user.has_perms(['blog.add_post', 'blog.change_post']):
        pass
    
    if request.user.is_superuser:
        pass


# ============================================
# 6. 认证 Mixin
# ============================================

from django.views.generic import ListView, DetailView, UpdateView


class MyPostsView(LoginRequiredMixin, ListView):
    """
    我的文章列表（需要登录）
    """
    model = Post
    template_name = 'blog/my_posts.html'
    login_url = '/login/'
    
    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)


class PostUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    更新文章（需要登录和权限）
    """
    model = Post
    fields = ['title', 'content']
    template_name = 'blog/post_form.html'
    permission_required = 'blog.change_post'
    login_url = '/login/'
    
    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)


# ============================================
# 7. 用户资料管理
# ============================================

from django import forms


class ProfileForm(forms.ModelForm):
    """
    用户资料表单
    """
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'bio', 'website', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
        }


@login_required
def profile_edit(request):
    """
    编辑个人资料
    """
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '个人资料已更新！✨')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    
    return render(request, 'blog/profile_edit.html', {'form': form})


# ============================================
# 8. 密码管理
# ============================================

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


@login_required
def change_password(request):
    """
    修改密码
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, '密码修改成功！')
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'blog/change_password.html', {'form': form})


# ============================================
# 9. 密码重置
# ============================================
"""
Django 内置的密码重置视图：

# urls.py

from django.contrib.auth import views as auth_views

urlpatterns = [
    # 密码重置
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset.html',
             email_template_name='registration/password_reset_email.html',
             success_url='/password_reset/done/'
         ),
         name='password_reset'),
    
    # 密码重置邮件已发送
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),
    
    # 密码重置确认
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url='/reset/done/'
         ),
         name='password_reset_confirm'),
    
    # 密码重置完成
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]
"""

# ============================================
# 10. 权限和组
# ============================================

def manage_permissions():
    """
    权限管理示例
    """
    # 创建组
    editors_group, created = Group.objects.get_or_create(name='Editors')
    
    # 获取权限
    add_post_perm = Permission.objects.get(codename='add_post')
    change_post_perm = Permission.objects.get(codename='change_post')
    delete_post_perm = Permission.objects.get(codename='delete_post')
    
    # 给组添加权限
    editors_group.permissions.add(add_post_perm, change_post_perm)
    
    # 给用户添加权限
    user = User.objects.get(username='xiaoming')
    user.user_permissions.add(add_post_perm)
    
    # 将用户加入组
    user.groups.add(editors_group)
    
    # 检查用户权限
    if user.has_perm('blog.add_post'):
        print('用户有创建文章的权限')
    
    # 检查组权限
    if user.groups.filter(name='Editors').exists():
        print('用户是编辑组成员')


# ============================================
# 11. 登录模板示例
# ============================================
"""
templates/registration/login.html:

{% extends 'base.html' %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card shadow">
            <div class="card-body">
                <h2 class="card-title text-center mb-4">🔐 用户登录</h2>
                
                {% if messages %}
                    {% for message in messages %}
                    <div class="alert alert-{{ message.tags }}">
                        {{ message }}
                    </div>
                    {% endfor %}
                {% endif %}
                
                <form method="post">
                    {% csrf_token %}
                    
                    <div class="mb-3">
                        <label for="username" class="form-label">用户名</label>
                        <input type="text" class="form-control" id="username" 
                               name="username" required>
                    </div>
                    
                    <div class="mb-3">
                        <label for="password" class="form-label">密码</label>
                        <input type="password" class="form-control" id="password" 
                               name="password" required>
                    </div>
                    
                    <div class="mb-3 form-check">
                        <input type="checkbox" class="form-check-input" 
                               id="remember" name="remember">
                        <label class="form-check-label" for="remember">
                            记住我
                        </label>
                    </div>
                    
                    <button type="submit" class="btn btn-primary w-100">
                        登录 🚀
                    </button>
                </form>
                
                <hr>
                
                <div class="text-center">
                    <a href="{% url 'password_reset' %}">忘记密码？</a>
                    <span class="mx-2">|</span>
                    <a href="{% url 'signup' %}">注册账号</a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# ============================================
# 12. URL 配置
# ============================================
"""
# urls.py

from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 认证相关
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    
    # 用户资料
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('password/change/', views.change_password, name='change_password'),
    
    # 密码重置
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(), 
         name='password_reset'),
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(), 
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(), 
         name='password_reset_complete'),
]
"""

# ============================================
# 13. settings.py 配置
# ============================================
"""
# 认证相关配置

# 自定义用户模型
AUTH_USER_MODEL = 'blog.CustomUser'

# 登录 URL
LOGIN_URL = '/login/'

# 登录成功后重定向 URL
LOGIN_REDIRECT_URL = '/'

# 登出后重定向 URL
LOGOUT_REDIRECT_URL = '/'

# 密码验证器
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# 会话配置
SESSION_COOKIE_AGE = 1209600  # 2 周（秒）
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True
"""

# ============================================
# 练习任务
# ============================================
"""
1. 创建自定义用户模型，添加手机号和头像字段

2. 实现用户注册功能：
   - 注册表单
   - 密码确认
   - 邮箱验证

3. 实现用户登录功能：
   - 登录表单
   - 记住我功能
   - 登录后重定向

4. 实现用户资料管理：
   - 查看个人资料
   - 编辑个人资料
   - 修改密码

5. 实现密码重置功能：
   - 发送重置邮件
   - 重置密码
"""

if __name__ == "__main__":
    print("亲爱的主人，这是 Django 用户认证系统的学习笔记~ 🌸")
    print("请按照上面的步骤学习用户认证！")
    print("\n关键概念：")
    print("  - User 模型：用户数据")
    print("  - authenticate()：验证用户")
    print("  - login()：登录用户")
    print("  - logout()：登出用户")
    print("  - @login_required：登录装饰器")
    print("  - 权限和组：访问控制")
