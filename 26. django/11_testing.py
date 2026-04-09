"""
Django 学习笔记 11 - 测试
=====================================

亲爱的主人，让我们学习 Django 的测试框架！🧪
"""

# ============================================
# 1. 测试概述
# ============================================
"""
Django 提供了完整的测试框架：
    ✅ 单元测试
    ✅ 集成测试
    ✅ 客户端测试
    ✅ 数据库测试
    ✅ 表单测试
    ✅ 视图测试
"""

# ============================================
# 2. 测试文件结构
# ============================================
"""
blog/
├── tests/
│   ├── __init__.py
│   ├── test_models.py      # 模型测试
│   ├── test_views.py       # 视图测试
│   ├── test_forms.py       # 表单测试
│   └── test_api.py         # API 测试
└── tests.py                # 简单测试可以放这里
"""

# ============================================
# 3. 基础测试示例
# ============================================

from django.test import TestCase
from django.contrib.auth.models import User
from .models import Post, Category, Tag


class PostModelTest(TestCase):
    """
    文章模型测试
    """
    
    def setUp(self):
        """
        测试前准备
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Django',
            slug='django'
        )
        self.post = Post.objects.create(
            title='测试文章',
            slug='test-post',
            author=self.user,
            content='这是测试内容',
            category=self.category,
            status='published'
        )
    
    def test_post_creation(self):
        """
        测试文章创建
        """
        self.assertEqual(self.post.title, '测试文章')
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.status, 'published')
        self.assertTrue(isinstance(self.post, Post))
    
    def test_post_str(self):
        """
        测试 __str__ 方法
        """
        self.assertEqual(str(self.post), '测试文章')
    
    def test_post_get_absolute_url(self):
        """
        测试获取绝对 URL
        """
        url = self.post.get_absolute_url()
        self.assertIn('test-post', url)
    
    def test_post_ordering(self):
        """
        测试文章排序
        """
        post2 = Post.objects.create(
            title='第二篇文章',
            slug='second-post',
            author=self.user,
            content='内容',
            status='published'
        )
        posts = Post.objects.all()
        self.assertEqual(posts[0], post2)  # 最新的在前面


class CategoryModelTest(TestCase):
    """
    分类模型测试
    """
    
    def setUp(self):
        self.category = Category.objects.create(
            name='Python',
            slug='python',
            description='Python 相关文章'
        )
    
    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Python')
        self.assertEqual(self.category.slug, 'python')
    
    def test_category_unique_slug(self):
        """
        测试 slug 唯一性
        """
        with self.assertRaises(Exception):
            Category.objects.create(
                name='Python 2',
                slug='python'  # 重复的 slug
            )


# ============================================
# 4. 视图测试
# ============================================

from django.urls import reverse


class PostViewTest(TestCase):
    """
    文章视图测试
    """
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.post = Post.objects.create(
            title='测试文章',
            slug='test-post',
            author=self.user,
            content='测试内容',
            status='published'
        )
    
    def test_post_list_view(self):
        """
        测试文章列表视图
        """
        response = self.client.get(reverse('blog:post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_list.html')
        self.assertContains(response, '测试文章')
    
    def test_post_detail_view(self):
        """
        测试文章详情视图
        """
        response = self.client.get(self.post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '测试文章')
        self.assertContains(response, '测试内容')
    
    def test_post_create_view_login_required(self):
        """
        测试创建文章需要登录
        """
        response = self.client.get(reverse('blog:post_create'))
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"/login/?next={reverse('blog:post_create')}")
    
    def test_post_create_view_authenticated(self):
        """
        测试登录后可以创建文章
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('blog:post_create'))
        self.assertEqual(response.status_code, 200)
    
    def test_post_update_by_author(self):
        """
        测试作者可以更新文章
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('blog:post_update', args=[self.post.id])
        )
        self.assertEqual(response.status_code, 200)
    
    def test_post_update_by_non_author(self):
        """
        测试非作者不能更新文章
        """
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        self.client.login(username='otheruser', password='otherpass123')
        response = self.client.get(
            reverse('blog:post_update', args=[self.post.id])
        )
        self.assertEqual(response.status_code, 403)


# ============================================
# 5. 表单测试
# ============================================

from .forms import PostForm, CommentForm


class PostFormTest(TestCase):
    """
    文章表单测试
    """
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Django',
            slug='django'
        )
    
    def test_valid_form(self):
        """
        测试有效表单
        """
        data = {
            'title': '测试文章',
            'slug': 'test-post',
            'content': '测试内容',
            'status': 'published',
            'category': self.category.id,
        }
        form = PostForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_form_no_title(self):
        """
        测试无效表单（无标题）
        """
        data = {
            'title': '',
            'content': '测试内容',
        }
        form = PostForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_invalid_form_short_title(self):
        """
        测试标题太短
        """
        data = {
            'title': 'AB',  # 太短
            'content': '测试内容',
        }
        form = PostForm(data=data)
        self.assertFalse(form.is_valid())


class CommentFormTest(TestCase):
    """
    评论表单测试
    """
    
    def test_valid_comment_form(self):
        data = {'content': '这是一条评论'}
        form = CommentForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_comment_form_empty(self):
        data = {'content': ''}
        form = CommentForm(data=data)
        self.assertFalse(form.is_valid())


# ============================================
# 6. 客户端测试
# ============================================

from django.test import Client


class ClientTest(TestCase):
    """
    客户端测试
    """
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_home_page(self):
        """
        测试首页
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_login(self):
        """
        测试登录
        """
        response = self.client.login(
            username='testuser',
            password='testpass123'
        )
        self.assertTrue(response)
    
    def test_login_with_wrong_password(self):
        """
        测试错误密码登录
        """
        response = self.client.login(
            username='testuser',
            password='wrongpassword'
        )
        self.assertFalse(response)
    
    def test_post_creation_via_post(self):
        """
        测试通过 POST 创建文章
        """
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            reverse('blog:post_create'),
            {
                'title': '新文章',
                'slug': 'new-post',
                'content': '新内容',
                'status': 'published',
            }
        )
        
        # 检查是否重定向
        self.assertEqual(response.status_code, 302)
        
        # 检查文章是否创建
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.first().title, '新文章')


# ============================================
# 7. 测试数据库
# ============================================

class DatabaseTest(TestCase):
    """
    数据库测试
    """
    
    def test_user_creation(self):
        """
        测试用户创建
        """
        User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='newpass123'
        )
        self.assertEqual(User.objects.count(), 1)
    
    def test_post_with_tags(self):
        """
        测试文章和标签的多对多关系
        """
        user = User.objects.create_user(username='test', password='test')
        post = Post.objects.create(
            title='测试',
            slug='test',
            author=user,
            content='内容'
        )
        
        tag1 = Tag.objects.create(name='Python', slug='python')
        tag2 = Tag.objects.create(name='Django', slug='django')
        
        post.tags.add(tag1, tag2)
        
        self.assertEqual(post.tags.count(), 2)
        self.assertIn(tag1, post.tags.all())


# ============================================
# 8. 测试信号
# ============================================

class SignalTest(TestCase):
    """
    信号测试
    """
    
    def test_post_save_signal(self):
        """
        测试文章保存信号
        """
        user = User.objects.create_user(username='test', password='test')
        
        with self.assertLogs('blog.signals', level='INFO') as cm:
            post = Post.objects.create(
                title='测试',
                slug='test',
                author=user,
                content='内容'
            )
            
            # 检查日志是否被记录
            self.assertIn('文章创建', cm.output[0])


# ============================================
# 9. 测试中间件
# ============================================

class MiddlewareTest(TestCase):
    """
    中间件测试
    """
    
    def test_request_logging_middleware(self):
        """
        测试请求日志中间件
        """
        response = self.client.get('/')
        
        # 检查响应头
        self.assertIn('X-Request-Duration', response)


# ============================================
# 10. 测试异常
# ============================================

class ExceptionTest(TestCase):
    """
    异常测试
    """
    
    def test_404_error(self):
        """
        测试 404 错误
        """
        response = self.client.get('/nonexistent/')
        self.assertEqual(response.status_code, 404)
    
    def test_permission_denied(self):
        """
        测试权限拒绝
        """
        user = User.objects.create_user(username='test', password='test')
        post = Post.objects.create(
            title='测试',
            slug='test',
            author=user,
            content='内容'
        )
        
        other_user = User.objects.create_user(
            username='other',
            password='other'
        )
        self.client.login(username='other', password='other')
        
        response = self.client.get(
            reverse('blog:post_update', args=[post.id])
        )
        self.assertEqual(response.status_code, 403)


# ============================================
# 11. 测试覆盖率
# ============================================
"""
# 安装 coverage
pip install coverage

# 运行测试并收集覆盖率数据
coverage run manage.py test

# 生成覆盖率报告
coverage report

# 生成 HTML 报告
coverage html

# 查看 HTML 报告
# 打开 htmlcov/index.html

# .coveragerc 配置文件
[run]
source = .
omit = 
    */migrations/*
    */tests/*
    */__init__.py
    manage.py

[report]
exclude_lines =
    pragma: no cover
    def __str__
    raise NotImplementedError
"""

# ============================================
# 12. 测试夹具（Fixtures）
# ============================================
"""
# 创建夹具
python manage.py dumpdata blog > fixtures/blog_data.json

# 加载夹具
python manage.py loaddata fixtures/blog_data.json

# tests.py 中使用夹具

class PostViewTest(TestCase):
    fixtures = ['blog_data.json']
    
    def test_with_fixture(self):
        # 夹具数据已加载
        posts = Post.objects.all()
        self.assertTrue(posts.exists())
"""

# ============================================
# 13. 测试最佳实践
# ============================================
"""
1. 测试命名规范
   - 测试类以 Test 结尾
   - 测试方法以 test_ 开头
   - 使用描述性的测试名称

2. 测试独立性
   - 每个测试应该独立运行
   - 不要依赖其他测试的结果
   - 使用 setUp 和 tearDown

3. 测试覆盖率
   - 目标：80% 以上的覆盖率
   - 测试所有关键路径
   - 测试边界条件和异常情况

4. 使用工厂模式
   - 使用 factory_boy 创建测试数据
   - 避免重复的数据创建代码

5. 测试速度
   - 使用内存数据库加速测试
   - 避免不必要的数据库操作
   - 使用 mock 模拟外部依赖

6. 持续集成
   - 在 CI/CD 中运行测试
   - 测试失败时阻止部署
"""

# ============================================
# 14. 运行测试
# ============================================
"""
# 运行所有测试
python manage.py test

# 运行特定应用的测试
python manage.py test blog

# 运行特定测试文件
python manage.py test blog.tests.test_models

# 运行特定测试类
python manage.py test blog.tests.test_models.PostModelTest

# 运行特定测试方法
python manage.py test blog.tests.test_models.PostModelTest.test_post_creation

# 显示更多输出
python manage.py test --verbosity=2

# 并行运行测试
python manage.py test --parallel

# 保留测试数据库
python manage.py test --keepdb

# 失败时停止
python manage.py test --failfast
"""

# ============================================
# 练习任务
# ============================================
"""
1. 为你的模型编写测试：
   - 测试创建、更新、删除
   - 测试模型方法
   - 测试约束和验证

2. 为你的视图编写测试：
   - 测试页面访问
   - 测试登录要求
   - 测试权限控制

3. 为你的表单编写测试：
   - 测试有效数据
   - 测试无效数据
   - 测试验证逻辑

4. 使用 coverage 检查测试覆盖率

5. 编写集成测试
"""

if __name__ == "__main__":
    print("亲爱的主人，这是 Django 测试的学习笔记~ 🌸")
    print("请按照上面的步骤学习测试！")
    print("\n关键命令：")
    print("  python manage.py test")
    print("  coverage run manage.py test")
    print("  coverage report")
