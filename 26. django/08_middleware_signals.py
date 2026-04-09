"""
Django 学习笔记 08 - 中间件和信号
=====================================

亲爱的主人，让我们学习 Django 的中间件和信号机制！🔧
"""

# ============================================
# 1. 中间件概述
# ============================================
"""
中间件是一个轻量级、底层的插件系统，用于在全局范围内修改 Django 的输入和输出。

中间件的作用：
    ✅ 在请求到达视图之前处理请求
    ✅ 在响应返回客户端之前处理响应
    ✅ 全局异常处理
    ✅ 请求日志记录
    ✅ 用户认证
    ✅ CORS 处理
"""

# ============================================
# 2. 中间件执行流程
# ============================================
"""
请求处理流程：

Request → Middleware 1 → Middleware 2 → ... → View
                                                    ↓
Response ← Middleware 1 ← Middleware 2 ← ... ← ← ←

执行顺序：
1. 请求阶段：从上到下执行 process_request
2. 视图阶段：执行 process_view
3. 响应阶段：从下到上执行 process_response
4. 异常阶段：从下到上执行 process_exception
"""

# ============================================
# 3. 自定义中间件
# ============================================

from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
import time
import logging

logger = logging.getLogger(__name__)


class SimpleMiddleware(MiddlewareMixin):
    """
    简单中间件示例
    """
    
    def __init__(self, get_response):
        """
        初始化（只执行一次）
        """
        self.get_response = get_response
        print("SimpleMiddleware 初始化")
    
    def __call__(self, request):
        """
        处理请求和响应
        """
        # 请求前的处理
        print(f"请求路径: {request.path}")
        
        # 获取响应
        response = self.get_response(request)
        
        # 响应后的处理
        print(f"响应状态码: {response.status_code}")
        
        return response
    
    def process_request(self, request):
        """
        处理请求（在视图之前）
        返回 None：继续处理
        返回 HttpResponse：中断请求
        """
        print("process_request 执行")
        return None
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        处理视图（在视图函数之前）
        """
        print(f"process_view 执行: {view_func.__name__}")
        return None
    
    def process_response(self, request, response):
        """
        处理响应（在视图之后）
        必须返回 response
        """
        print("process_response 执行")
        return response
    
    def process_exception(self, request, exception):
        """
        处理异常（当视图抛出异常时）
        返回 None：继续抛出异常
        返回 HttpResponse：使用该响应
        """
        logger.error(f"请求异常: {exception}")
        return None


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    请求日志中间件
    """
    
    def __call__(self, request):
        # 记录请求信息
        logger.info(f"[{request.method}] {request.path} - User: {request.user}")
        
        start_time = time.time()
        response = self.get_response(request)
        end_time = time.time()
        
        # 记录响应信息
        duration = (end_time - start_time) * 1000
        logger.info(f"[Response] {response.status_code} - {duration:.2f}ms")
        
        # 添加响应头
        response['X-Request-Duration'] = f"{duration:.2f}ms"
        
        return response


class BlockIPMiddleware(MiddlewareMixin):
    """
    IP 黑名单中间件
    """
    
    BLOCKED_IPS = [
        '192.168.1.100',
        '10.0.0.50',
    ]
    
    def process_request(self, request):
        ip = self.get_client_ip(request)
        
        if ip in self.BLOCKED_IPS:
            return HttpResponse("您的 IP 已被封禁", status=403)
        
        return None
    
    def get_client_ip(self, request):
        """获取客户端 IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class CORSMiddleware(MiddlewareMixin):
    """
    CORS 跨域中间件
    """
    
    def process_response(self, request, response):
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        if request.method == 'OPTIONS':
            response.status_code = 200
        
        return response


class MaintenanceModeMiddleware(MiddlewareMixin):
    """
    维护模式中间件
    """
    
    MAINTENANCE_MODE = False
    ALLOWED_PATHS = ['/admin/', '/health/']
    
    def process_request(self, request):
        if not self.MAINTENANCE_MODE:
            return None
        
        for path in self.ALLOWED_PATHS:
            if request.path.startswith(path):
                return None
        
        return HttpResponse(
            "系统维护中，请稍后再试...",
            status=503,
            content_type='text/plain; charset=utf-8'
        )


# ============================================
# 4. 中间件注册
# ============================================
"""
# settings.py

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # 自定义中间件
    'blog.middleware.RequestLoggingMiddleware',
    'blog.middleware.BlockIPMiddleware',
    'blog.middleware.CORSMiddleware',
    'blog.middleware.MaintenanceModeMiddleware',
]

注意：中间件的顺序很重要！
- SecurityMiddleware 应该在最前面
- AuthenticationMiddleware 应该在需要用户认证的中间件之前
"""

# ============================================
# 5. 内置中间件
# ============================================
"""
Django 内置中间件：

1. SecurityMiddleware
   - SSL 重定向
   - HSTS 头
   - 点击劫持保护

2. SessionMiddleware
   - 会话管理
   - Cookie 处理

3. CommonMiddleware
   - URL 规范化
   - APPEND_SLASH 处理

4. CsrfViewMiddleware
   - CSRF 保护

5. AuthenticationMiddleware
   - 用户认证
   - request.user

6. MessageMiddleware
   - 消息框架

7. XFrameOptionsMiddleware
   - 点击劫持保护
"""

# ============================================
# 6. 信号机制概述
# ============================================
"""
信号允许某些发送者通知一组接收者某些操作已经发生。

Django 内置信号：
    - pre_init / post_init: 模型实例化前后
    - pre_save / post_save: 模型保存前后
    - pre_delete / post_delete: 模型删除前后
    - m2m_changed: 多对多关系改变
    - request_started / request_finished: 请求开始/结束
    - got_request_exception: 请求异常
"""

# ============================================
# 7. 模型信号
# ============================================

from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User


@receiver(pre_save, sender=Post)
def pre_save_post(sender, instance, **kwargs):
    """
    文章保存前
    """
    print(f"文章即将保存: {instance.title}")
    
    # 自动生成摘要
    if not instance.excerpt and instance.content:
        instance.excerpt = instance.content[:200] + '...'


@receiver(post_save, sender=Post)
def post_save_post(sender, instance, created, **kwargs):
    """
    文章保存后
    """
    if created:
        print(f"新文章创建: {instance.title}")
        # 发送通知
        send_notification(instance)
    else:
        print(f"文章更新: {instance.title}")


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    创建用户时自动创建资料
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    保存用户时保存资料
    """
    instance.profile.save()


@receiver(pre_delete, sender=Post)
def pre_delete_post(sender, instance, **kwargs):
    """
    文章删除前
    """
    print(f"文章即将删除: {instance.title}")
    # 记录删除日志
    log_deletion(instance)


@receiver(post_delete, sender=Post)
def post_delete_post(sender, instance, **kwargs):
    """
    文章删除后
    """
    print(f"文章已删除: {instance.title}")
    # 清理相关数据
    cleanup_related_data(instance)


# ============================================
# 8. 多对多信号
# ============================================

from django.db.models.signals import m2m_changed


@receiver(m2m_changed, sender=Post.tags.through)
def tags_changed(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    文章标签变化
    """
    if action == "post_add":
        print(f"添加标签: {pk_set}")
    elif action == "post_remove":
        print(f"移除标签: {pk_set}")
    elif action == "post_clear":
        print("清空所有标签")


# ============================================
# 9. 请求信号
# ============================================

from django.core.signals import request_started, request_finished, got_request_exception


@receiver(request_started)
def on_request_started(sender, environ, **kwargs):
    """
    请求开始
    """
    print(f"请求开始: {environ.get('PATH_INFO')}")


@receiver(request_finished)
def on_request_finished(sender, **kwargs):
    """
    请求结束
    """
    print("请求结束")


@receiver(got_request_exception)
def on_request_exception(sender, request, **kwargs):
    """
    请求异常
    """
    logger.error(f"请求异常: {request.path}")


# ============================================
# 10. 自定义信号
# ============================================

from django.dispatch import Signal


# 定义信号
post_published = Signal()
comment_added = Signal()
user_registered = Signal()


# 发送信号
def publish_post(post):
    """发布文章"""
    post.status = 'published'
    post.save()
    
    # 发送信号
    post_published.send(
        sender=Post,
        instance=post,
        author=post.author
    )


# 接收信号
@receiver(post_published)
def on_post_published(sender, instance, author, **kwargs):
    """文章发布后处理"""
    print(f"文章已发布: {instance.title}")
    
    # 发送通知
    send_notification_to_subscribers(instance)
    
    # 更新统计
    update_statistics(author)


@receiver(post_published)
def log_publication(sender, instance, **kwargs):
    """记录发布日志"""
    logger.info(f"文章发布: {instance.title} by {instance.author}")


# ============================================
# 11. 信号注册方式
# ============================================
"""
方式一：使用 @receiver 装饰器（推荐）

@receiver(post_save, sender=Post)
def my_handler(sender, instance, **kwargs):
    pass


方式二：手动连接

def my_handler(sender, instance, **kwargs):
    pass

post_save.connect(my_handler, sender=Post)


方式三：在 apps.py 中注册

# blog/apps.py

from django.apps import AppConfig

class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
    
    def ready(self):
        # 导入信号处理器
        import blog.signals


# blog/__init__.py

default_app_config = 'blog.apps.BlogConfig'
"""

# ============================================
# 12. 信号最佳实践
# ============================================
"""
1. 避免在信号中执行耗时操作
   - 使用 Celery 异步处理

2. 注意信号循环
   - 在信号中保存模型可能触发另一个信号

3. 使用 weak=False 防止信号被垃圾回收
   - post_save.connect(handler, weak=False)

4. 在 apps.py 的 ready() 中导入信号

5. 使用自定义信号解耦应用

6. 记录信号处理日志

7. 处理异常避免影响主流程
"""

# ============================================
# 13. 实战示例：访问统计中间件
# ============================================

class PageViewMiddleware(MiddlewareMixin):
    """
    页面访问统计中间件
    """
    
    EXCLUDED_PATHS = ['/admin/', '/static/', '/media/', '/favicon.ico']
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # 排除特定路径
        for path in self.EXCLUDED_PATHS:
            if request.path.startswith(path):
                return response
        
        # 记录访问
        if request.user.is_authenticated:
            PageView.objects.create(
                user=request.user,
                path=request.path,
                method=request.method,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                status_code=response.status_code
            )
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')


# ============================================
# 练习任务
# ============================================
"""
1. 创建请求日志中间件，记录所有请求信息

2. 创建 IP 黑名单中间件，阻止特定 IP 访问

3. 使用信号实现：
   - 用户注册时发送欢迎邮件
   - 文章发布时通知订阅者
   - 评论添加时更新评论数

4. 创建自定义信号，用于应用间通信

5. 实现访问统计功能
"""

if __name__ == "__main__":
    print("亲爱的主人，这是 Django 中间件和信号的学习笔记~ 🌸")
    print("请按照上面的步骤学习中间件和信号！")
    print("\n关键概念：")
    print("  - 中间件：请求/响应处理链")
    print("  - 信号：事件驱动机制")
    print("  - @receiver：信号接收器装饰器")
