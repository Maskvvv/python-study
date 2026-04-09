"""
Django 学习笔记 04 - 模板系统
=====================================

亲爱的主人，让我们学习 Django 强大的模板系统！🎨
"""

# ============================================
# 1. 模板基础
# ============================================
"""
Django 模板是一个文本文件，用于生成任何基于文本的格式（HTML、XML、CSV 等）。

模板包含：
    - 静态内容：HTML 标签、文本等
    - 动态内容：模板变量、标签、过滤器等
"""

# ============================================
# 2. 模板配置
# ============================================
"""
# settings.py

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # 模板目录
        'APP_DIRS': True,  # 在应用的 templates 目录中查找
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

目录结构：
myproject/
├── templates/              # 全局模板目录
│   ├── base.html
│   └── pages/
│       └── home.html
└── blog/
    └── templates/          # 应用模板目录
        └── blog/
            ├── post_list.html
            └── post_detail.html
"""

# ============================================
# 3. 模板变量
# ============================================
"""
模板变量用双花括号包裹：{{ variable }}

视图：
def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    return render(request, 'blog/post_detail.html', {'post': post})

模板：
<h1>{{ post.title }}</h1>
<p>作者：{{ post.author.username }}</p>
<p>发布时间：{{ post.publish }}</p>
<p>浏览次数：{{ post.views }}</p>

变量支持：
    - 字典查询：{{ dict.key }}
    - 属性查询：{{ object.attribute }}
    - 方法调用：{{ object.method }}  # 不需要括号
    - 列表索引：{{ list.0 }}
"""

# ============================================
# 4. 模板标签
# ============================================
"""
模板标签用花括号和百分号包裹：{% tag %}
"""

# 4.1 for 循环
"""
{% for post in posts %}
    <div class="post">
        <h2>{{ post.title }}</h2>
        <p>{{ post.content|truncatewords:30 }}</p>
    </div>
{% empty %}
    <p>暂无文章</p>
{% endfor %}

for 循环变量：
    - forloop.counter: 当前循环次数（从 1 开始）
    - forloop.counter0: 当前循环次数（从 0 开始）
    - forloop.revcounter: 剩余循环次数（从 1 开始）
    - forloop.revcounter0: 剩余循环次数（从 0 开始）
    - forloop.first: 是否为第一次循环
    - forloop.last: 是否为最后一次循环
    - forloop.parentloop: 父级循环对象

示例：
{% for post in posts %}
    <div class="post {% if forloop.first %}first{% endif %}">
        {{ forloop.counter }}. {{ post.title }}
    </div>
{% endfor %}
"""

# 4.2 if 条件
"""
{% if post.status == 'published' %}
    <span class="badge">已发布</span>
{% elif post.status == 'draft' %}
    <span class="badge draft">草稿</span>
{% else %}
    <span class="badge unknown">未知状态</span>
{% endif %}

支持的运算符：
    - ==, !=, <, >, <=, >=
    - in, not in
    - and, or, not
    
{% if user.is_authenticated %}
    <p>欢迎，{{ user.username }}！</p>
{% endif %}

{% if post in featured_posts %}
    <span>精选文章</span>
{% endif %}
"""

# 4.3 url 标签
"""
<a href="{% url 'blog:post_list' %}">文章列表</a>

<a href="{% url 'blog:post_detail' post.id %}">{{ post.title }}</a>

<a href="{% url 'blog:category' category.slug %}">{{ category.name }}</a>

带查询参数：
{% url 'blog:post_list' %}?page=2
"""

# 4.4 static 标签
"""
{% load static %}

<link rel="stylesheet" href="{% static 'css/style.css' %}">
<script src="{% static 'js/main.js' %}"></script>
<img src="{% static 'images/logo.png' %}" alt="Logo">
"""

# 4.5 include 标签
"""
{% include 'navbar.html' %}

{% include 'card.html' with title="推荐文章" posts=featured_posts %}
"""

# 4.6 block 和 extends（模板继承）
"""
base.html:
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}我的网站{% endblock %}</title>
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% include 'navbar.html' %}
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    {% include 'footer.html' %}
    
    {% block extra_js %}{% endblock %}
</body>
</html>

post_list.html:
{% extends 'base.html' %}

{% block title %}文章列表 - {{ block.super }}{% endblock %}

{% block content %}
    <h1>文章列表</h1>
    {% for post in posts %}
        <div class="post">
            <h2>{{ post.title }}</h2>
        </div>
    {% endfor %}
{% endblock %}

{% block extra_css %}
    <link rel="stylesheet" href="{% static 'css/post.css' %}">
{% endblock %}
"""

# ============================================
# 5. 模板过滤器
# ============================================
"""
过滤器修改变量的显示方式：{{ variable|filter }}
"""

# 5.1 常用过滤器
"""
{{ name|lower }}                    # 转换为小写
{{ name|upper }}                    # 转换为大写
{{ name|title }}                    # 首字母大写
{{ name|capfirst }}                 # 第一个字母大写

{{ text|truncatewords:30 }}         # 截断为 30 个单词
{{ text|truncatechars:100 }}        # 截断为 100 个字符

{{ content|linebreaks }}            # 将换行符转换为 <p> 和 <br>
{{ content|linebreaksbr }}          # 将换行符转换为 <br>

{{ text|striptags }}                # 去除 HTML 标签
{{ text|safe }}                     # 不转义 HTML（谨慎使用）

{{ date|date:"Y-m-d H:i:s" }}       # 格式化日期
{{ date|timesince }}                # 距今多久

{{ value|default:"默认值" }}        # 如果为空，显示默认值
{{ value|default_if_none:"默认值" }} # 如果为 None，显示默认值

{{ value|yesno:"是,否,未知" }}      # 布尔值转换为文本

{{ list|length }}                   # 列表长度
{{ list|join:", " }}                # 用逗号连接列表元素

{{ number|add:5 }}                  # 加法
{{ number|divisibleby:2 }}          # 是否能被 2 整除

{{ value|floatformat:2 }}           # 保留 2 位小数
"""

# 5.2 链式过滤
"""
{{ post.content|striptags|truncatewords:50 }}
{{ post.title|default:"无标题"|upper }}
"""

# ============================================
# 6. 完整模板示例
# ============================================

# templates/base.html
BASE_HTML = """
{% load static %}
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}我的博客{% endblock %}</title>
    <link rel="stylesheet" href="{% static 'css/bootstrap.min.css' %}">
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- 导航栏 -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{% url 'blog:post_list' %}">
                🌸 我的博客
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'blog:post_list' %}">首页</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'blog:about' %}">关于</a>
                    </li>
                </ul>
                <ul class="navbar-nav">
                    {% if user.is_authenticated %}
                        <li class="nav-item">
                            <a class="nav-link" href="#">{{ user.username }}</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'logout' %}">退出</a>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'login' %}">登录</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'register' %}">注册</a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <!-- 主内容 -->
    <main class="container my-4">
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}
        
        {% block content %}{% endblock %}
    </main>

    <!-- 页脚 -->
    <footer class="bg-dark text-white py-4 mt-5">
        <div class="container text-center">
            <p>&copy; 2024 我的博客. Made with 💖 by Django</p>
        </div>
    </footer>

    <script src="{% static 'js/bootstrap.bundle.min.js' %}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
"""

# templates/blog/post_list.html
POST_LIST_HTML = """
{% extends 'base.html' %}
{% load static %}

{% block title %}文章列表 - {{ block.super }}{% endblock %}

{% block content %}
<div class="row">
    <!-- 文章列表 -->
    <div class="col-lg-8">
        <h1 class="mb-4">📝 文章列表</h1>
        
        {% for post in posts %}
        <article class="card mb-4 shadow-sm">
            <div class="card-body">
                <h2 class="card-title">
                    <a href="{{ post.get_absolute_url }}" class="text-decoration-none">
                        {{ post.title }}
                    </a>
                </h2>
                <p class="card-text text-muted">
                    <small>
                        <i class="bi bi-person"></i> {{ post.author.username }}
                        <i class="bi bi-calendar ms-2"></i> {{ post.publish|date:"Y年m月d日" }}
                        <i class="bi bi-eye ms-2"></i> {{ post.views }} 次浏览
                    </small>
                </p>
                <p class="card-text">
                    {{ post.content|striptags|truncatechars:200 }}
                </p>
                <a href="{{ post.get_absolute_url }}" class="btn btn-primary">
                    阅读更多 →
                </a>
            </div>
        </article>
        {% empty %}
        <div class="alert alert-info">
            <h4>暂无文章 😢</h4>
            <p>亲爱的主人，还没有发布任何文章哦~</p>
        </div>
        {% endfor %}
        
        <!-- 分页 -->
        {% if page_obj.has_other_pages %}
        <nav aria-label="分页">
            <ul class="pagination justify-content-center">
                {% if page_obj.has_previous %}
                <li class="page-item">
                    <a class="page-link" href="?page={{ page_obj.previous_page_number }}">上一页</a>
                </li>
                {% endif %}
                
                {% for num in page_obj.paginator.page_range %}
                    {% if page_obj.number == num %}
                    <li class="page-item active">
                        <span class="page-link">{{ num }}</span>
                    </li>
                    {% else %}
                    <li class="page-item">
                        <a class="page-link" href="?page={{ num }}">{{ num }}</a>
                    </li>
                    {% endif %}
                {% endfor %}
                
                {% if page_obj.has_next %}
                <li class="page-item">
                    <a class="page-link" href="?page={{ page_obj.next_page_number }}">下一页</a>
                </li>
                {% endif %}
            </ul>
        </nav>
        {% endif %}
    </div>
    
    <!-- 侧边栏 -->
    <div class="col-lg-4">
        {% include 'blog/sidebar.html' %}
    </div>
</div>
{% endblock %}
"""

# templates/blog/post_detail.html
POST_DETAIL_HTML = """
{% extends 'base.html' %}
{% load static %}

{% block title %}{{ post.title }} - {{ block.super }}{% endblock %}

{% block content %}
<article>
    <header class="mb-4">
        <h1 class="display-5">{{ post.title }}</h1>
        <div class="text-muted mb-3">
            <span><i class="bi bi-person"></i> {{ post.author.username }}</span>
            <span class="ms-3"><i class="bi bi-calendar"></i> {{ post.publish|date:"Y年m月d日 H:i" }}</span>
            <span class="ms-3"><i class="bi bi-eye"></i> {{ post.views }} 次浏览</span>
        </div>
        <div class="mb-3">
            {% if post.category %}
            <a href="{{ post.category.get_absolute_url }}" class="badge bg-primary text-decoration-none">
                {{ post.category.name }}
            </a>
            {% endif %}
            {% for tag in post.tags.all %}
            <a href="{{ tag.get_absolute_url }}" class="badge bg-secondary text-decoration-none">
                {{ tag.name }}
            </a>
            {% endfor %}
        </div>
    </header>
    
    <div class="post-content">
        {{ post.content|linebreaks }}
    </div>
    
    <!-- 点赞和分享 -->
    <div class="d-flex justify-content-between align-items-center my-4 py-3 border-top border-bottom">
        <div>
            <button class="btn btn-outline-primary" id="like-btn">
                <i class="bi bi-heart"></i> 点赞 ({{ post.likes }})
            </button>
        </div>
        <div>
            <span>分享到：</span>
            <a href="#" class="btn btn-sm btn-outline-secondary">微信</a>
            <a href="#" class="btn btn-sm btn-outline-secondary">微博</a>
        </div>
    </div>
    
    <!-- 上一篇/下一篇 -->
    <div class="row my-4">
        <div class="col-6">
            {% if previous_post %}
            <a href="{{ previous_post.get_absolute_url }}" class="text-decoration-none">
                ← {{ previous_post.title|truncatechars:20 }}
            </a>
            {% endif %}
        </div>
        <div class="col-6 text-end">
            {% if next_post %}
            <a href="{{ next_post.get_absolute_url }}" class="text-decoration-none">
                {{ next_post.title|truncatechars:20 }} →
            </a>
            {% endif %}
        </div>
    </div>
    
    <!-- 相关文章 -->
    {% if related_posts %}
    <section class="my-4">
        <h3>相关文章</h3>
        <div class="row">
            {% for related in related_posts %}
            <div class="col-md-4 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">
                            <a href="{{ related.get_absolute_url }}">{{ related.title }}</a>
                        </h5>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </section>
    {% endif %}
    
    <!-- 评论区 -->
    <section class="mt-5">
        <h3>💬 评论 ({{ post.comments.count }})</h3>
        
        <!-- 评论表单 -->
        {% if user.is_authenticated %}
        <form method="post" action="{% url 'blog:comment_add' post.id %}" class="mb-4">
            {% csrf_token %}
            <div class="mb-3">
                <textarea name="content" class="form-control" rows="3" 
                          placeholder="写下你的评论..." required></textarea>
            </div>
            <button type="submit" class="btn btn-primary">发表评论</button>
        </form>
        {% else %}
        <div class="alert alert-info">
            <a href="{% url 'login' %}?next={{ request.path }}">登录</a> 后才能评论哦~
        </div>
        {% endif %}
        
        <!-- 评论列表 -->
        <div class="comments">
            {% for comment in post.comments.all %}
            <div class="comment border-bottom py-3">
                <div class="d-flex justify-content-between">
                    <strong>{{ comment.author.username }}</strong>
                    <small class="text-muted">{{ comment.created_at|timesince }}前</small>
                </div>
                <p class="mb-0 mt-2">{{ comment.content }}</p>
            </div>
            {% empty %}
            <p class="text-muted">暂无评论，快来抢沙发吧~ 🛋️</p>
            {% endfor %}
        </div>
    </section>
</article>
{% endblock %}

{% block extra_js %}
<script>
document.getElementById('like-btn').addEventListener('click', function() {
    fetch('{% url "blog:post_like" post.id %}', {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}',
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    });
});
</script>
{% endblock %}
"""

# ============================================
# 7. 自定义模板标签和过滤器
# ============================================

# blog/templatetags/blog_tags.py

from django import template
from ..models import Post, Category, Tag

register = template.Library()


@register.simple_tag
def total_posts():
    """返回文章总数"""
    return Post.objects.filter(status='published').count()


@register.inclusion_tag('blog/latest_posts.html')
def show_latest_posts(count=5):
    """显示最新文章"""
    latest_posts = Post.objects.filter(
        status='published'
    ).order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


@register.simple_tag
def get_most_viewed_posts(count=5):
    """获取浏览最多的文章"""
    return Post.objects.filter(
        status='published'
    ).order_by('-views')[:count]


@register.filter(name='markdown')
def markdown_filter(text):
    """Markdown 过滤器"""
    import markdown
    return markdown.markdown(text, extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
    ])


@register.filter
def reading_time(text, wpm=200):
    """计算阅读时间（字数/每分钟阅读字数）"""
    word_count = len(text)
    minutes = word_count // wpm
    if minutes == 0:
        return '1 分钟阅读'
    return f'{minutes} 分钟阅读'


# 使用自定义标签：
"""
{% load blog_tags %}

{% total_posts %} 篇文章

{% show_latest_posts 10 %}

{% get_most_viewed_posts 5 as popular_posts %}
{% for post in popular_posts %}
    {{ post.title }}
{% endfor %}

{{ post.content|markdown }}
{{ post.content|reading_time }}
"""

# ============================================
# 练习任务
# ============================================
"""
1. 创建基础模板 base.html，包含导航栏和页脚

2. 创建文章列表模板 post_list.html，显示所有文章

3. 创建文章详情模板 post_detail.html，显示文章内容和评论

4. 创建自定义模板标签：
   - 显示最新文章
   - 显示热门文章
   - 计算阅读时间

5. 使用模板继承创建多个页面模板
"""

if __name__ == "__main__":
    print("亲爱的主人，这是 Django 模板系统的学习笔记~ 🌸")
    print("请按照上面的步骤创建你的模板文件！")
    print("\n关键概念：")
    print("  - 模板变量：{{ variable }}")
    print("  - 模板标签：{% tag %}")
    print("  - 模板过滤器：{{ variable|filter }}")
    print("  - 模板继承：{% extends 'base.html' %}")
