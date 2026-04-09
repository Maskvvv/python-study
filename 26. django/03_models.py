"""
Django 学习笔记 03 - 模型（Model）
=====================================

亲爱的主人，让我们学习 Django 强大的 ORM 模型系统！💫
"""

# ============================================
# 1. 什么是 ORM？
# ============================================
"""
ORM（Object-Relational Mapping）对象关系映射：
    - 用 Python 类来定义数据库表
    - 用类属性来定义字段
    - 用对象方法来操作数据
    - 无需编写 SQL 语句

优点：
    ✅ 数据库无关性（可轻松切换数据库）
    ✅ 避免 SQL 注入
    ✅ 代码更易维护
    ✅ 提高开发效率
"""

# ============================================
# 2. 定义模型
# ============================================

# blog/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    """
    文章分类模型
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
        from django.urls import reverse
        return reverse('blog:category', args=[self.slug])


class Tag(models.Model):
    """
    文章标签模型
    """
    name = models.CharField('标签名称', max_length=50)
    slug = models.SlugField('URL 别名', unique=True)
    
    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Post(models.Model):
    """
    文章模型
    """
    # 文章状态选择
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
    
    # 分类和标签
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name='分类'
    )
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='标签')
    
    # 状态和时间
    status = models.CharField(
        '状态',
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft'
    )
    publish = models.DateTimeField('发布时间', default=timezone.now)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    # 统计数据
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
        from django.urls import reverse
        return reverse('blog:post_detail', args=[
            self.publish.year,
            self.publish.month,
            self.publish.day,
            self.slug
        ])


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
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    active = models.BooleanField('是否显示', default=True)
    
    # 回复功能
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
# 3. 字段类型
# ============================================
"""
常用字段类型：

数值类型：
    - IntegerField: 整数
    - BigIntegerField: 大整数
    - SmallIntegerField: 小整数
    - PositiveIntegerField: 正整数
    - FloatField: 浮点数
    - DecimalField: 十进制数（精确计算）

字符串类型：
    - CharField: 字符串（必须指定 max_length）
    - TextField: 长文本
    - SlugField: URL 友好字符串
    - EmailField: 邮箱
    - URLField: URL
    - FileField: 文件上传
    - ImageField: 图片上传

布尔类型：
    - BooleanField: 布尔值
    - NullBooleanField: 可为空的布尔值

日期时间类型：
    - DateField: 日期
    - TimeField: 时间
    - DateTimeField: 日期时间
    - DurationField: 时间段

关系类型：
    - ForeignKey: 一对多关系
    - ManyToManyField: 多对多关系
    - OneToOneField: 一对一关系

其他类型：
    - UUIDField: UUID
    - GenericIPAddressField: IP 地址
    - JSONField: JSON 数据
    - BinaryField: 二进制数据
"""

# ============================================
# 4. 字段参数
# ============================================
"""
通用参数：
    - null: 是否允许为空（数据库层面）
    - blank: 是否允许为空（表单验证层面）
    - default: 默认值
    - verbose_name: 人类可读的名称
    - help_text: 帮助文本
    - unique: 是否唯一
    - db_index: 是否创建索引
    - editable: 是否可编辑
    - choices: 选择项
    
字符串字段特有：
    - max_length: 最大长度
    
数值字段特有：
    - max_value: 最大值
    - min_value: 最小值
    
日期时间字段特有：
    - auto_now: 每次保存时自动更新
    - auto_now_add: 创建时自动设置
    
关系字段特有：
    - on_delete: 删除行为
        - CASCADE: 级联删除
        - PROTECT: 禁止删除
        - SET_NULL: 设置为空
        - SET_DEFAULT: 设置为默认值
        - DO_NOTHING: 不做任何操作
    - related_name: 反向关系名称
    - limit_choices_to: 限制可选对象
"""

# ============================================
# 5. 数据库迁移
# ============================================
"""
# 创建迁移文件
python manage.py makemigrations

# 查看迁移 SQL
python manage.py sqlmigrate blog 0001

# 执行迁移
python manage.py migrate

# 查看迁移状态
python manage.py showmigrations

# 回滚迁移
python manage.py migrate blog 0001

# 伪造迁移（标记为已执行）
python manage.py migrate --fake blog 0001
"""

# ============================================
# 6. QuerySet API - 查询数据
# ============================================

# 创建数据
"""
# 方法一：create()
post = Post.objects.create(
    title='我的第一篇文章',
    slug='my-first-post',
    author=user,
    content='这是文章内容...',
    status='published'
)

# 方法二：实例化后保存
post = Post(
    title='我的第一篇文章',
    slug='my-first-post',
    author=user,
    content='这是文章内容...',
    status='published'
)
post.save()

# 方法三：get_or_create() - 获取或创建
post, created = Post.objects.get_or_create(
    slug='my-first-post',
    defaults={
        'title': '我的第一篇文章',
        'author': user,
        'content': '这是文章内容...',
    }
)
"""

# 查询数据
"""
# 获取所有数据
posts = Post.objects.all()

# 过滤数据
published_posts = Post.objects.filter(status='published')
draft_posts = Post.objects.exclude(status='published')

# 链式查询
posts = Post.objects.filter(
    status='published'
).filter(
    category__name='Django'
).order_by('-publish')

# 获取单个对象
post = Post.objects.get(id=1)
post = Post.objects.get(slug='my-first-post')

# 获取或返回 404
from django.shortcuts import get_object_or_404
post = get_object_or_404(Post, slug='my-first-post')

# 获取第一个/最后一个
first_post = Post.objects.first()
last_post = Post.objects.last()

# 计数
count = Post.objects.count()
count = Post.objects.filter(status='published').count()

# 存在性检查
exists = Post.objects.filter(title='测试').exists()

# 字段查询
posts = Post.objects.filter(title__exact='测试')          # 精确匹配
posts = Post.objects.filter(title__iexact='测试')         # 不区分大小写
posts = Post.objects.filter(title__contains='Django')     # 包含
posts = Post.objects.filter(title__icontains='django')    # 包含（不区分大小写）
posts = Post.objects.filter(title__startswith='我的')      # 以...开头
posts = Post.objects.filter(title__endswith='教程')        # 以...结尾
posts = Post.objects.filter(publish__year=2024)           # 年份
posts = Post.objects.filter(publish__month=1)             # 月份
posts = Post.objects.filter(publish__date__gte='2024-01-01')  # 日期比较
posts = Post.objects.filter(views__gt=100)                # 大于
posts = Post.objects.filter(views__gte=100)               # 大于等于
posts = Post.objects.filter(views__lt=100)                # 小于
posts = Post.objects.filter(views__lte=100)               # 小于等于
posts = Post.objects.filter(views__in=[10, 20, 30])       # 在列表中
posts = Post.objects.filter(views__range=[10, 100])       # 范围

# 关联查询
posts = Post.objects.filter(author__username='admin')
posts = Post.objects.filter(category__name='Django')
posts = Post.objects.filter(tags__name='Python')

# 排序
posts = Post.objects.order_by('publish')          # 升序
posts = Post.objects.order_by('-publish')         # 降序
posts = Post.objects.order_by('category', '-publish')  # 多字段排序

# 去重
posts = Post.objects.distinct()

# 限制结果数量
posts = Post.objects.all()[:5]      # 前 5 条
posts = Post.objects.all()[5:10]    # 第 6-10 条

# 聚合查询
from django.db.models import Count, Sum, Avg, Max, Min

# 统计数量
category_count = Category.objects.annotate(
    post_count=Count('posts')
)

# 聚合
stats = Post.objects.aggregate(
    total_views=Sum('views'),
    avg_views=Avg('views'),
    max_views=Max('views'),
    min_views=Min('views'),
    total_posts=Count('id')
)

# 分组统计
from django.db.models import Count
posts_by_category = Post.objects.values('category__name').annotate(
    count=Count('id')
)
"""

# 更新数据
"""
# 更新单个对象
post = Post.objects.get(id=1)
post.title = '新的标题'
post.save()

# 批量更新
Post.objects.filter(status='draft').update(status='published')

# 更新字段
post.views = models.F('views') + 1  # 使用 F() 表达式
post.save()

Post.objects.update(views=models.F('views') + 1)
"""

# 删除数据
"""
# 删除单个对象
post = Post.objects.get(id=1)
post.delete()

# 批量删除
Post.objects.filter(status='draft').delete()
"""

# ============================================
# 7. 模型方法
# ============================================

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        """字符串表示"""
        return self.title
    
    def get_absolute_url(self):
        """获取对象的绝对 URL"""
        from django.urls import reverse
        return reverse('article_detail', args=[self.id])
    
    def increase_views(self):
        """增加浏览次数"""
        self.views += 1
        self.save(update_fields=['views'])
    
    def get_summary(self, length=100):
        """获取文章摘要"""
        if len(self.content) > length:
            return self.content[:length] + '...'
        return self.content
    
    @property
    def is_popular(self):
        """是否为热门文章"""
        return self.views > 1000
    
    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
        ordering = ['-created_at']


# ============================================
# 8. 模型管理器
# ============================================

class PublishedManager(models.Manager):
    """自定义管理器 - 只返回已发布的文章"""
    
    def get_queryset(self):
        return super().get_queryset().filter(status='published')


class AdvancedPost(models.Model):
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
    ]
    
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    
    # 默认管理器
    objects = models.Manager()
    # 自定义管理器
    published = PublishedManager()
    
    class Meta:
        verbose_name = '高级文章'
        verbose_name_plural = '高级文章'


# 使用示例：
# AdvancedPost.objects.all()           # 所有文章
# AdvancedPost.published.all()         # 只返回已发布的文章

# ============================================
# 练习任务
# ============================================
"""
1. 创建一个博客应用，包含以下模型：
   - Category（分类）
   - Tag（标签）
   - Post（文章）
   - Comment（评论）

2. 为每个模型添加合适的字段和关系

3. 执行数据库迁移

4. 使用 Django Shell 测试 CRUD 操作：
   python manage.py shell
   
   from blog.models import Post, Category
   from django.contrib.auth.models import User
   
   # 创建分类
   category = Category.objects.create(name='Django', slug='django')
   
   # 创建文章
   user = User.objects.first()
   post = Post.objects.create(
       title='Django 学习笔记',
       slug='django-notes',
       author=user,
       content='这是内容...',
       category=category,
       status='published'
   )
   
   # 查询文章
   posts = Post.objects.filter(status='published')
   print(posts)
"""

if __name__ == "__main__":
    print("亲爱的主人，这是 Django 模型的学习笔记~ 🌸")
    print("请按照上面的步骤创建你的数据模型！")
    print("\n关键命令：")
    print("  python manage.py makemigrations")
    print("  python manage.py migrate")
    print("  python manage.py shell")
