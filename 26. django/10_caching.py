"""
Django 学习笔记 10 - 缓存系统
=====================================

亲爱的主人，让我们学习 Django 强大的缓存系统！⚡
"""

# ============================================
# 1. 缓存概述
# ============================================
"""
缓存可以显著提高网站性能：
    ✅ 减少数据库查询
    ✅ 减少计算开销
    ✅ 提高响应速度
    ✅ 降低服务器负载

Django 支持多种缓存后端：
    - 内存缓存（Memcached）
    - 数据库缓存
    - 文件系统缓存
    - 本地内存缓存
    - Redis 缓存
"""

# ============================================
# 2. 缓存配置
# ============================================
"""
# settings.py

# 本地内存缓存（开发环境）
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# 数据库缓存
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}

# 创建缓存表
python manage.py createcachetable

# 文件系统缓存
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
    }
}

# Memcached
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

# Redis（推荐）
# pip install django-redis

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# 缓存超时时间（秒）
CACHE_MIDDLEWARE_SECONDS = 600
"""

# ============================================
# 3. 视图缓存
# ============================================

from django.views.decorators.cache import cache_page
from django.shortcuts import render


@cache_page(60 * 15)  # 缓存 15 分钟
def post_list(request):
    """
    缓存整个视图
    """
    posts = Post.objects.filter(status='published')
    return render(request, 'blog/post_list.html', {'posts': posts})


@cache_page(60 * 5, key_prefix='user_posts')
def user_posts(request, username):
    """
    带前缀的视图缓存
    """
    posts = Post.objects.filter(author__username=username)
    return render(request, 'blog/user_posts.html', {'posts': posts})


# URL 配置中使用缓存
from django.urls import path
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('posts/', cache_page(60 * 10)(views.post_list), name='post_list'),
]


# ============================================
# 4. 模板片段缓存
# ============================================
"""
# 模板中使用缓存

{% load cache %}
{% cache 500 sidebar request.user.username %}
    <!-- 缓存 500 秒 -->
    <div class="sidebar">
        <h3>热门文章</h3>
        {% for post in popular_posts %}
            <a href="{{ post.get_absolute_url }}">{{ post.title }}</a>
        {% endfor %}
    </div>
{% endcache %}

# 带多个参数的缓存键

{% cache 500 sidebar request.user.username request.GET.page %}
    ...
{% endcache %}

# 使用缓存键前缀

{% cache 500 sidebar request.user.username using="sidebar_cache" %}
    ...
{% endcache %}
"""

# ============================================
# 5. 低级缓存 API
# ============================================

from django.core.cache import cache
from django.shortcuts import get_object_or_404


def get_post(post_id):
    """
    使用缓存获取文章
    """
    cache_key = f'post_{post_id}'
    post = cache.get(cache_key)
    
    if post is None:
        # 缓存未命中，从数据库获取
        post = get_object_or_404(Post, id=post_id)
        # 设置缓存（15 分钟）
        cache.set(cache_key, post, 60 * 15)
    
    return post


def update_post(post_id, data):
    """
    更新文章并清除缓存
    """
    post = Post.objects.get(id=post_id)
    post.title = data.get('title', post.title)
    post.content = data.get('content', post.content)
    post.save()
    
    # 清除缓存
    cache_key = f'post_{post_id}'
    cache.delete(cache_key)
    
    return post


def get_or_set_cache(key, func, timeout=300):
    """
    获取或设置缓存
    """
    value = cache.get(key)
    
    if value is None:
        value = func()
        cache.set(key, value, timeout)
    
    return value


# 使用示例
def get_popular_posts():
    return get_or_set_cache(
        'popular_posts',
        lambda: Post.objects.filter(views__gt=1000).order_by('-views')[:10],
        timeout=60 * 30
    )


# ============================================
# 6. 缓存操作
# ============================================

def cache_operations():
    """
    缓存基本操作
    """
    # 设置缓存
    cache.set('my_key', 'my_value', 60)  # 60 秒
    
    # 获取缓存
    value = cache.get('my_key')
    value = cache.get('my_key', 'default_value')  # 带默认值
    
    # 批量设置
    cache.set_many({
        'key1': 'value1',
        'key2': 'value2',
        'key3': 'value3',
    })
    
    # 批量获取
    values = cache.get_many(['key1', 'key2', 'key3'])
    
    # 删除缓存
    cache.delete('my_key')
    
    # 批量删除
    cache.delete_many(['key1', 'key2'])
    
    # 清空所有缓存
    cache.clear()
    
    # 添加（仅当键不存在时）
    cache.add('new_key', 'new_value', 60)
    
    # 获取或设置
    value = cache.get_or_set('my_key', 'default', 60)
    
    # 自增/自减
    cache.set('counter', 10)
    cache.incr('counter')  # 11
    cache.incr('counter', 5)  # 16
    cache.decr('counter')  # 15
    
    # 检查键是否存在
    if 'my_key' in cache:
        print('键存在')
    
    # 设置过期时间
    cache.touch('my_key', 120)  # 更新为 120 秒


# ============================================
# 7. 缓存装饰器
# ============================================

from django.core.cache import cache
from functools import wraps


def cache_result(timeout=300, key_prefix=''):
    """
    缓存函数结果装饰器
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f'{key_prefix}:{func.__name__}:{args}:{kwargs}'
            
            # 尝试从缓存获取
            result = cache.get(cache_key)
            
            if result is None:
                # 执行函数
                result = func(*args, **kwargs)
                # 存入缓存
                cache.set(cache_key, result, timeout)
            
            return result
        
        return wrapper
    return decorator


# 使用示例
@cache_result(timeout=60 * 10, key_prefix='blog')
def get_category_posts(category_id):
    """
    获取分类文章（带缓存）
    """
    return Post.objects.filter(
        category_id=category_id,
        status='published'
    ).order_by('-publish')


# ============================================
# 8. 查询缓存
# ============================================

from django.db import models


class CachedQuerySet(models.QuerySet):
    """
    带缓存的查询集
    """
    def cached_get(self, *args, **kwargs):
        """
        缓存 get 查询
        """
        cache_key = f'cached_get:{self.model.__name__}:{args}:{kwargs}'
        obj = cache.get(cache_key)
        
        if obj is None:
            obj = self.get(*args, **kwargs)
            cache.set(cache_key, obj, 60 * 15)
        
        return obj
    
    def cached_filter(self, *args, **kwargs):
        """
        缓存 filter 查询
        """
        cache_key = f'cached_filter:{self.model.__name__}:{args}:{kwargs}'
        objs = cache.get(cache_key)
        
        if objs is None:
            objs = list(self.filter(*args, **kwargs))
            cache.set(cache_key, objs, 60 * 15)
        
        return objs


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    objects = CachedQuerySet.as_manager()


# ============================================
# 9. 缓存失效策略
# ============================================

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


@receiver(post_save, sender=Post)
def invalidate_post_cache(sender, instance, **kwargs):
    """
    文章保存时清除相关缓存
    """
    # 清除文章详情缓存
    cache.delete(f'post_{instance.id}')
    
    # 清除文章列表缓存
    cache.delete('post_list')
    
    # 清除分类文章缓存
    if instance.category:
        cache.delete(f'category_posts_{instance.category_id}')
    
    # 清除用户文章缓存
    cache.delete(f'user_posts_{instance.author_id}')
    
    # 清除热门文章缓存
    cache.delete('popular_posts')


@receiver(post_delete, sender=Post)
def invalidate_post_cache_on_delete(sender, instance, **kwargs):
    """
    文章删除时清除相关缓存
    """
    cache.delete(f'post_{instance.id}')
    cache.delete('post_list')


# ============================================
# 10. 缓存中间件
# ============================================
"""
# settings.py

MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',  # 必须在最前面
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',  # 必须在 UpdateCacheMiddleware 之后
    ...
]

CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 600
CACHE_MIDDLEWARE_KEY_PREFIX = 'myapp'

# 按视图设置缓存
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True  # 只缓存匿名用户请求
"""

# ============================================
# 11. Redis 高级用法
# ============================================
"""
# settings.py

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': [
            'redis://127.0.0.1:6379/1',  # 主服务器
            'redis://127.0.0.1:6379/2',  # 从服务器
        ],
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
            },
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        },
        'KEY_PREFIX': 'myapp:',
    }
}

# 使用 Redis 连接
from django_redis import get_redis_connection

def redis_operations():
    r = get_redis_connection('default')
    
    # 字符串操作
    r.set('key', 'value')
    r.get('key')
    
    # 哈希操作
    r.hset('user:1', 'name', 'Alice')
    r.hget('user:1', 'name')
    r.hgetall('user:1')
    
    # 列表操作
    r.lpush('posts', 'post1', 'post2')
    r.rpop('posts')
    r.lrange('posts', 0, -1)
    
    # 集合操作
    r.sadd('tags', 'python', 'django')
    r.smembers('tags')
    
    # 有序集合
    r.zadd('rank', {'user1': 100, 'user2': 200})
    r.zrange('rank', 0, -1, withscores=True)
    
    # 发布订阅
    r.publish('channel', 'message')
"""

# ============================================
# 12. 缓存最佳实践
# ============================================
"""
1. 选择合适的缓存粒度
   - 页面缓存：适合静态页面
   - 片段缓存：适合动态页面的静态部分
   - 对象缓存：适合数据库查询结果

2. 合理设置过期时间
   - 热点数据：较长的过期时间
   - 频繁更新的数据：较短的过期时间

3. 及时清除缓存
   - 数据更新时清除相关缓存
   - 使用信号自动清除缓存

4. 避免缓存雪崩
   - 设置随机的过期时间
   - 使用互斥锁防止缓存击穿

5. 监控缓存性能
   - 缓存命中率
   - 内存使用情况
   - 响应时间

6. 使用合适的缓存后端
   - 开发环境：本地内存缓存
   - 生产环境：Redis 或 Memcached
"""

# ============================================
# 13. 缓存示例：热门文章
# ============================================

def get_hot_posts(days=7, limit=10):
    """
    获取热门文章（带缓存）
    """
    from datetime import timedelta
    from django.utils import timezone
    
    cache_key = f'hot_posts_{days}_{limit}'
    posts = cache.get(cache_key)
    
    if posts is None:
        start_date = timezone.now() - timedelta(days=days)
        posts = list(
            Post.objects.filter(
                status='published',
                publish__gte=start_date
            ).annotate(
                score=models.Count('views') + models.Count('comments') * 5
            ).order_by('-score')[:limit]
        )
        cache.set(cache_key, posts, 60 * 30)
    
    return posts


# ============================================
# 练习任务
# ============================================
"""
1. 配置 Redis 缓存后端

2. 实现视图缓存：
   - 缓存文章列表页
   - 缓存文章详情页

3. 实现模板片段缓存：
   - 缓存侧边栏
   - 缓存导航栏

4. 使用低级缓存 API：
   - 缓存数据库查询结果
   - 缓存计算结果

5. 实现缓存失效机制：
   - 数据更新时清除缓存
   - 使用信号自动清除
"""

if __name__ == "__main__":
    print("亲爱的主人，这是 Django 缓存系统的学习笔记~ 🌸")
    print("请按照上面的步骤学习缓存系统！")
    print("\n关键概念：")
    print("  - cache_page：视图缓存装饰器")
    print("  - {% cache %}：模板片段缓存")
    print("  - cache.set/get：低级缓存 API")
    print("  - Redis：推荐的缓存后端")
