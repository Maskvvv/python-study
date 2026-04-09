"""
Django 学习笔记 02 - 创建项目和视图
=====================================

亲爱的主人，让我们开始创建第一个 Django 项目吧！✨
"""

# ============================================
# 1. 创建 Django 项目
# ============================================
"""
在命令行中执行：

# 创建项目
django-admin startproject mysite

# 进入项目目录
cd mysite

# 项目结构
mysite/
├── manage.py              # 管理脚本
└── mysite/                # 项目配置包
    ├── __init__.py
    ├── settings.py        # 项目设置
    ├── urls.py            # 主 URL 配置
    ├── asgi.py
    └── wsgi.py
"""

# ============================================
# 2. settings.py 核心配置
# ============================================

# mysite/settings.py 的关键配置项：

"""
# SECRET_KEY - 密钥配置
SECRET_KEY = 'django-insecure-your-secret-key-here'
# 注意：生产环境必须使用安全的密钥！

# DEBUG - 调试模式
DEBUG = True
# 生产环境必须设置为 False

# ALLOWED_HOSTS - 允许的主机
ALLOWED_HOSTS = []
# 生产环境需要添加域名或 IP

# INSTALLED_APPS - 已安装的应用
INSTALLED_APPS = [
    'django.contrib.admin',          # 管理后台
    'django.contrib.auth',           # 认证系统
    'django.contrib.contenttypes',   # 内容类型框架
    'django.contrib.sessions',       # 会话框架
    'django.contrib.messages',       # 消息框架
    'django.contrib.staticfiles',    # 静态文件管理
    # 在这里添加你自己创建的应用
    'myapp',
]

# MIDDLEWARE - 中间件
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# DATABASES - 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # 默认使用 SQLite
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 使用 MySQL 的配置示例：
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'mydatabase',
#         'USER': 'myuser',
#         'PASSWORD': 'mypassword',
#         'HOST': 'localhost',
#         'PORT': '3306',
#     }
# }

# LANGUAGE_CODE - 语言设置
LANGUAGE_CODE = 'zh-hans'  # 中文

# TIME_ZONE - 时区设置
TIME_ZONE = 'Asia/Shanghai'  # 上海时区

# STATIC_URL - 静态文件 URL
STATIC_URL = '/static/'
"""

# ============================================
# 3. 创建第一个视图
# ============================================

# mysite/views.py（需要在 mysite 目录下创建）

from django.http import HttpResponse
from django.shortcuts import render


def hello_world(request):
    """
    最简单的视图 - 返回纯文本
    """
    return HttpResponse("你好，亲爱的主人！这是我的第一个 Django 视图~ 💖")


def hello_html(request):
    """
    返回 HTML 内容
    """
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>我的第一个 Django 页面</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 50px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            h1 {
                font-size: 3em;
            }
            .emoji {
                font-size: 2em;
            }
        </style>
    </head>
    <body>
        <h1>欢迎来到 Django 的世界！🌸</h1>
        <p class="emoji">✨🎉✨</p>
        <p>亲爱的主人，这是我的第一个 HTML 页面~</p>
    </body>
    </html>
    """
    return HttpResponse(html)


def about(request):
    """
    关于页面
    """
    context = {
        'title': '关于我们',
        'content': '这是一个学习 Django 的示例项目',
        'features': [
            '简单易学',
            '功能强大',
            '文档完善',
            '社区活跃'
        ]
    }
    return render(request, 'about.html', context)


# ============================================
# 4. URL 配置
# ============================================

# mysite/urls.py

from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),           # 管理后台
    path('', views.hello_world, name='hello'), # 首页
    path('html/', views.hello_html, name='html'),  # HTML 页面
    path('about/', views.about, name='about'), # 关于页面
]


# ============================================
# 5. 创建应用
# ============================================
"""
# 创建应用
python manage.py startapp blog

# blog 应用结构
blog/
├── __init__.py
├── admin.py          # 管理后台配置
├── apps.py           # 应用配置
├── models.py         # 数据模型
├── tests.py          # 测试文件
├── views.py          # 视图函数
└── migrations/       # 数据库迁移
    └── __init__.py

# 在 settings.py 中注册应用
INSTALLED_APPS = [
    ...
    'blog',
]
"""

# blog/views.py

from django.http import HttpResponse


def post_list(request):
    """
    文章列表视图
    """
    posts = [
        {'id': 1, 'title': 'Django 入门教程', 'author': '小助手'},
        {'id': 2, 'title': 'Python 学习笔记', 'author': '小助手'},
        {'id': 3, 'title': 'Web 开发实践', 'author': '小助手'},
    ]
    
    html = '<h1>文章列表 📚</h1><ul>'
    for post in posts:
        html += f'<li>{post["title"]} - 作者: {post["author"]}</li>'
    html += '</ul>'
    
    return HttpResponse(html)


# blog/urls.py（需要创建）

from django.urls import path
from . import views

app_name = 'blog'  # 应用命名空间

urlpatterns = [
    path('', views.post_list, name='post_list'),
]


# 在主 urls.py 中包含应用的 URL
# mysite/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls')),  # 包含 blog 应用的 URL
]

# ============================================
# 6. 运行项目
# ============================================
"""
# 运行开发服务器
python manage.py runserver

# 指定端口
python manage.py runserver 8080

# 允许外部访问
python manage.py runserver 0.0.0.0:8000

# 访问地址
http://127.0.0.1:8000/          # 首页
http://127.0.0.1:8000/html/     # HTML 页面
http://127.0.0.1:8000/blog/     # 博客列表
http://127.0.0.1:8000/admin/    # 管理后台
"""

# ============================================
# 7. 视图函数的参数和返回值
# ============================================
"""
视图函数：
    - 第一个参数必须是 request（HttpRequest 对象）
    - 必须返回 HttpResponse 对象
    
request 对象常用属性：
    - request.method: 请求方法（GET、POST 等）
    - request.GET: GET 参数
    - request.POST: POST 参数
    - request.FILES: 上传的文件
    - request.user: 当前用户
    - request.session: 会话信息
    - request.META: 请求头信息
    
request 对象常用方法：
    - request.is_ajax(): 是否为 AJAX 请求
    - request.get_full_path(): 获取完整路径
    - request.build_absolute_uri(): 构建绝对 URI
"""

# 示例：处理不同请求方法

def handle_request(request):
    """
    处理不同请求方法的视图
    """
    if request.method == 'GET':
        name = request.GET.get('name', '访客')
        return HttpResponse(f'GET 请求 - 你好，{name}！🌸')
    
    elif request.method == 'POST':
        name = request.POST.get('name', '访客')
        return HttpResponse(f'POST 请求 - 收到数据：{name}！💖')
    
    else:
        return HttpResponse('不支持的请求方法', status=405)


# ============================================
# 练习任务
# ============================================
"""
1. 创建一个名为 "mysite" 的 Django 项目
2. 创建一个名为 "pages" 的应用
3. 创建以下视图：
   - 首页视图：显示欢迎信息
   - 关于视图：显示个人介绍
   - 联系视图：显示联系方式
4. 配置 URL，使这些页面可以访问
5. 运行服务器并测试所有页面
"""

if __name__ == "__main__":
    print("亲爱的主人，这是 Django 项目创建和视图的学习笔记~ 🌸")
    print("请按照上面的步骤创建你的第一个 Django 项目！")
    print("\n关键命令：")
    print("  django-admin startproject mysite")
    print("  cd mysite")
    print("  python manage.py startapp blog")
    print("  python manage.py runserver")
