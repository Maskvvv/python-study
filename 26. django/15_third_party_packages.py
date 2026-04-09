"""
Django 学习笔记 15 - 常用第三方包
=====================================

亲爱的主人，让我为你介绍 Django 常用的第三方包！📦
"""

# ============================================
# 1. 开发工具
# ============================================

"""
1. django-debug-toolbar
   调试工具栏，显示请求、SQL 查询、缓存等信息
   
   pip install django-debug-toolbar
   
   # settings.py
   INSTALLED_APPS = [
       ...
       'debug_toolbar',
   ]
   
   MIDDLEWARE = [
       'debug_toolbar.middleware.DebugToolbarMiddleware',
       ...
   ]
   
   INTERNAL_IPS = ['127.0.0.1']
   
   # urls.py
   if settings.DEBUG:
       import debug_toolbar
       urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]


2. django-extensions
   Django 扩展工具集
   
   pip install django-extensions
   
   INSTALLED_APPS = [
       ...
       'django_extensions',
   ]
   
   常用命令：
   python manage.py shell_plus          # 增强的 shell
   python manage.py runserver_plus      # 增强的开发服务器
   python manage.py show_urls           # 显示所有 URL
   python manage.py graph_models        # 生成模型图
   python manage.py notes               # 显示 TODO 注释


3. django-cors-headers
   CORS 跨域支持
   
   pip install django-cors-headers
   
   INSTALLED_APPS = [
       ...
       'corsheaders',
   ]
   
   MIDDLEWARE = [
       'corsheaders.middleware.CorsMiddleware',
       ...
   ]
   
   CORS_ALLOWED_ORIGINS = [
       'https://example.com',
   ]
   
   CORS_ALLOW_ALL_ORIGINS = True  # 允许所有域名
"""

# ============================================
# 2. 表单和 UI
# ============================================

"""
1. django-crispy-forms
   美化表单渲染
   
   pip install django-crispy-forms
   pip install crispy-bootstrap5
   
   INSTALLED_APPS = [
       ...
       'crispy_forms',
       'crispy_bootstrap5',
   ]
   
   CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
   CRISPY_TEMPLATE_PACK = 'bootstrap5'
   
   # 模板中使用
   {% load crispy_forms_tags %}
   {{ form|crispy }}


2. django-widget-tweaks
   表单控件调整
   
   pip install django-widget-tweaks
   
   INSTALLED_APPS = [
       ...
       'widget_tweaks',
   ]
   
   # 模板中使用
   {% load widget_tweaks %}
   {{ form.title|add_class:"form-control" }}
   {{ form.title|attr:"placeholder:请输入标题" }}


3. django-ckeditor
   CKEditor 富文本编辑器
   
   pip install django-ckeditor
   
   INSTALLED_APPS = [
       ...
       'ckeditor',
   ]
   
   # models.py
   from ckeditor.fields import RichTextField
   
   class Post(models.Model):
       content = RichTextField('内容')
"""

# ============================================
# 3. 图片处理
# ============================================

"""
1. Pillow
   Python 图像处理库
   
   pip install Pillow
   
   # models.py
   from PIL import Image
   
   class Profile(models.Model):
       avatar = models.ImageField(upload_to='avatars/')
       
       def save(self, *args, **kwargs):
           super().save(*args, **kwargs)
           
           # 调整图片大小
           img = Image.open(self.avatar.path)
           if img.height > 300 or img.width > 300:
               img.thumbnail((300, 300))
               img.save(self.avatar.path)


2. django-imagekit
   图片处理工具
   
   pip install django-imagekit
   
   INSTALLED_APPS = [
       ...
       'imagekit',
   ]
   
   # models.py
   from imagekit.models import ImageSpecField
   from imagekit.processors import ResizeToFill
   
   class Post(models.Model):
       image = models.ImageField(upload_to='posts/')
       thumbnail = ImageSpecField(
           source='image',
           processors=[ResizeToFill(300, 200)],
           format='JPEG',
           options={'quality': 90}
       )
   
   # 模板中使用
   <img src="{{ post.thumbnail.url }}">
"""

# ============================================
# 4. 用户认证
# ============================================

"""
1. django-allauth
   完整的用户认证系统（支持社交登录）
   
   pip install django-allauth
   
   INSTALLED_APPS = [
       ...
       'django.contrib.sites',
       'allauth',
       'allauth.account',
       'allauth.socialaccount',
       'allauth.socialaccount.providers.google',
       'allauth.socialaccount.providers.github',
   ]
   
   SITE_ID = 1
   
   # urls.py
   path('accounts/', include('allauth.urls')),
   
   # settings.py
   ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
   ACCOUNT_EMAIL_REQUIRED = True
   ACCOUNT_EMAIL_VERIFICATION = 'mandatory'


2. django-guardian
   对象级权限控制
   
   pip install django-guardian
   
   INSTALLED_APPS = [
       ...
       'guardian',
   ]
   
   AUTHENTICATION_BACKENDS = (
       'django.contrib.auth.backends.ModelBackend',
       'guardian.backends.ObjectPermissionBackend',
   )
   
   # 使用
   from guardian.shortcuts import assign_perm, remove_perm
   
   assign_perm('change_post', user, post)
   user.has_perm('change_post', post)
"""

# ============================================
# 5. API 开发
# ============================================

"""
1. djangorestframework
   REST API 框架
   
   pip install djangorestframework
   
   INSTALLED_APPS = [
       ...
       'rest_framework',
   ]


2. drf-yasg
   API 文档生成
   
   pip install drf-yasg
   
   # urls.py
   from drf_yasg.views import get_schema_view
   from drf_yasg import openapi
   
   schema_view = get_schema_view(
       openapi.Info(
           title="API",
           default_version='v1',
       ),
       public=True,
   )
   
   urlpatterns = [
       path('swagger/', schema_view.with_ui('swagger')),
       path('redoc/', schema_view.with_ui('redoc')),
   ]


3. django-cors-headers
   CORS 支持（前面已介绍）
"""

# ============================================
# 6. 任务队列
# ============================================

"""
1. Celery
   分布式任务队列
   
   pip install celery
   pip install django-celery-beat
   pip install redis
   
   # myproject/celery.py
   import os
   from celery import Celery
   
   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
   app = Celery('myproject')
   app.config_from_object('django.conf:settings', namespace='CELERY')
   app.autodiscover_tasks()
   
   # settings.py
   CELERY_BROKER_URL = 'redis://localhost:6379/0'
   CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
   
   # tasks.py
   from celery import shared_task
   
   @shared_task
   def send_email_task(email):
       # 发送邮件逻辑
       pass
   
   # 视图中调用
   send_email_task.delay(user.email)


2. django-background-tasks
   简单的后台任务
   
   pip install django-background-tasks
   
   INSTALLED_APPS = [
       ...
       'background_task',
   ]
   
   # tasks.py
   from background_task import background
   
   @background(schedule=60)
   def send_email_task(email):
       # 发送邮件
       pass
   
   # 调用
   send_email_task(user.email)
"""

# ============================================
# 7. 搜索
# ============================================

"""
1. django-haystack
   全文搜索框架
   
   pip install django-haystack
   pip install whoosh
   
   INSTALLED_APPS = [
       ...
       'haystack',
   ]
   
   HAYSTACK_CONNECTIONS = {
       'default': {
           'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
           'PATH': os.path.join(BASE_DIR, 'whoosh_index'),
       },
   }
   
   # search_indexes.py
   from haystack import indexes
   from .models import Post
   
   class PostIndex(indexes.SearchIndex, indexes.Indexable):
       text = indexes.CharField(document=True, use_template=True)
       title = indexes.CharField(model_attr='title')
       
       def get_model(self):
           return Post
   
   # templates/search/indexes/blog/post_text.txt
   {{ object.title }}
   {{ object.content }}
   
   # 视图
   from haystack.query import SearchQuerySet
   
   def search(request):
       query = request.GET.get('q')
       results = SearchQuerySet().filter(content=query)
       return render(request, 'search.html', {'results': results})


2. django-elasticsearch-dsl
   Elasticsearch 集成
   
   pip install django-elasticsearch-dsl
   
   # settings.py
   ELASTICSEARCH_DSL = {
       'default': {
           'hosts': 'localhost:9200'
       },
   }
"""

# ============================================
# 8. 缓存
# ============================================

"""
1. django-redis
   Redis 缓存后端（前面已介绍）
   
   pip install django-redis
   
   CACHES = {
       'default': {
           'BACKEND': 'django_redis.cache.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
       }
   }
"""

# ============================================
# 9. 监控和日志
# ============================================

"""
1. sentry-sdk
   错误监控
   
   pip install sentry-sdk
   
   # settings.py
   import sentry_sdk
   from sentry_sdk.integrations.django import DjangoIntegration
   
   sentry_sdk.init(
       dsn='your-dsn',
       integrations=[DjangoIntegration()],
   )


2. django-prometheus
   Prometheus 监控
   
   pip install django-prometheus
   
   INSTALLED_APPS = [
       ...
       'django_prometheus',
   ]
   
   MIDDLEWARE = [
       'django_prometheus.middleware.PrometheusBeforeMiddleware',
       ...
       'django_prometheus.middleware.PrometheusAfterMiddleware',
   ]
   
   # urls.py
   path('', include('django_prometheus.urls')),
"""

# ============================================
# 10. 其他实用工具
# ============================================

"""
1. django-taggit
   标签系统
   
   pip install django-taggit
   
   INSTALLED_APPS = [
       ...
       'taggit',
   ]
   
   # models.py
   from taggit.managers import TaggableManager
   
   class Post(models.Model):
       tags = TaggableManager()


2. django-import-export
   数据导入导出
   
   pip install django-import-export
   
   INSTALLED_APPS = [
       ...
       'import_export',
   ]
   
   # admin.py
   from import_export.admin import ImportExportModelAdmin
   
   @admin.register(Post)
   class PostAdmin(ImportExportModelAdmin):
       pass


3. django-reversion
   版本控制
   
   pip install django-reversion
   
   INSTALLED_APPS = [
       ...
       'reversion',
   ]
   
   # admin.py
   from reversion.admin import VersionAdmin
   
   @admin.register(Post)
   class PostAdmin(VersionAdmin):
       pass


4. django-rosetta
   翻译管理
   
   pip install django-rosetta
   
   INSTALLED_APPS = [
       ...
       'rosetta',
   ]
   
   # urls.py
   path('rosetta/', include('rosetta.urls')),


5. django-robots
   robots.txt 管理
   
   pip install django-robots
   
   INSTALLED_APPS = [
       ...
       'robots',
   ]
   
   # urls.py
   path('robots.txt', include('robots.urls')),
"""

# ============================================
# 练习任务
# ============================================
"""
1. 安装并配置 django-debug-toolbar

2. 使用 django-crispy-forms 美化表单

3. 使用 django-ckeditor 添加富文本编辑器

4. 使用 django-allauth 实现社交登录

5. 使用 Celery 实现异步任务
"""

if __name__ == "__main__":
    print("亲爱的主人，这是 Django 常用第三方包的学习笔记~ 🌸")
    print("请根据需要选择安装这些包！")
    print("\n推荐安装：")
    print("  ✅ django-debug-toolbar（调试工具）")
    print("  ✅ django-crispy-forms（表单美化）")
    print("  ✅ django-ckeditor（富文本编辑）")
    print("  ✅ django-allauth（用户认证）")
    print("  ✅ djangorestframework（API 开发）")
