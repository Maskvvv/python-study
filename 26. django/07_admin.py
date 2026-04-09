"""
Django 学习笔记 07 - Admin 管理后台
=====================================

亲爱的主人，让我们学习 Django 强大的管理后台！✨
"""

# ============================================
# 1. Admin 后台概述
# ============================================
"""
Django Admin 是一个功能强大的后台管理系统：
    ✅ 自动生成管理界面
    ✅ 支持增删改查
    ✅ 可自定义显示
    ✅ 权限控制
    ✅ 搜索、过滤、排序
"""

# ============================================
# 2. 基本配置
# ============================================

# blog/admin.py

from django.contrib import admin
from .models import Post, Category, Tag, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    文章管理
    """
    list_display = ['title', 'author', 'category', 'status', 'publish', 'views']
    list_filter = ['status', 'category', 'tags', 'publish']
    search_fields = ['title', 'content', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']
    date_hierarchy = 'publish'
    ordering = ['-publish']
    list_per_page = 20
    list_editable = ['status']
    show_full_result_count = True
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'slug', 'author', 'category', 'tags')
        }),
        ('内容', {
            'fields': ('content', 'excerpt')
        }),
        ('状态和时间', {
            'fields': ('status', 'publish'),
            'classes': ('collapse',)
        }),
        ('统计数据', {
            'fields': ('views', 'likes'),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ['tags']
    
    def get_queryset(self, request):
        """只显示当前用户的文章（非超级管理员）"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)
    
    def save_model(self, request, obj, form, change):
        """自动设置作者"""
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    分类管理
    """
    list_display = ['name', 'slug', 'post_count', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    def post_count(self, obj):
        """统计文章数量"""
        return obj.posts.count()
    post_count.short_description = '文章数量'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    标签管理
    """
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    评论管理
    """
    list_display = ['author', 'post', 'created_at', 'active']
    list_filter = ['active', 'created_at']
    search_fields = ['author__username', 'content']
    actions = ['approve_comments', 'disapprove_comments']
    
    def approve_comments(self, request, queryset):
        """批量批准评论"""
        queryset.update(active=True)
    approve_comments.short_description = '批准选中的评论'
    
    def disapprove_comments(self, request, queryset):
        """批量取消批准"""
        queryset.update(active=False)
    disapprove_comments.short_description = '取消批准选中的评论'


# ============================================
# 3. ModelAdmin 选项
# ============================================
"""
列表显示选项：
    - list_display: 列表显示的字段
    - list_display_links: 可点击链接的字段
    - list_filter: 右侧过滤器
    - list_select_related: 关联查询优化
    - list_per_page: 每页显示数量
    - list_max_show_all: 全部显示的最大数量
    - list_editable: 可直接编辑的字段
    - search_fields: 搜索字段
    - date_hierarchy: 日期层级导航
    - ordering: 默认排序
    
表单选项：
    - fields: 显示的字段（顺序）
    - exclude: 排除的字段
    - fieldsets: 字段分组
    - filter_horizontal: 多对多字段水平过滤
    - filter_vertical: 多对多字段垂直过滤
    - raw_id_fields: 外键字段使用输入框
    - prepopulated_fields: 自动填充字段
    - readonly_fields: 只读字段
    
保存选项：
    - save_on_top: 顶部显示保存按钮
    - save_as: 另存为功能
    - save_as_continue: 保存后继续编辑
    
其他选项：
    - actions: 自定义操作
    - actions_on_top: 顶部显示操作栏
    - actions_on_bottom: 底部显示操作栏
    - actions_selection_counter: 显示选中数量
"""

# ============================================
# 4. 自定义 Admin 动作
# ============================================

def make_published(modeladmin, request, queryset):
    """批量发布文章"""
    count = queryset.update(status='published')
    modeladmin.message_user(request, f'成功发布 {count} 篇文章')
make_published.short_description = '发布选中的文章'


def make_draft(modeladmin, request, queryset):
    """批量设为草稿"""
    count = queryset.update(status='draft')
    modeladmin.message_user(request, f'已将 {count} 篇文章设为草稿')
make_draft.short_description = '设为草稿'


def export_as_csv(modeladmin, request, queryset):
    """导出为 CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="posts.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['标题', '作者', '状态', '发布时间', '浏览次数'])
    
    for post in queryset:
        writer.writerow([
            post.title,
            post.author.username,
            post.status,
            post.publish.strftime('%Y-%m-%d %H:%M'),
            post.views
        ])
    
    return response
export_as_csv.short_description = '导出为 CSV'


@admin.register(Post)
class PostAdminWithActions(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'publish']
    actions = [make_published, make_draft, export_as_csv]
    
    def get_actions(self, request):
        """根据权限显示动作"""
        actions = super().get_actions(request)
        if not request.user.has_perm('blog.can_publish'):
            if 'make_published' in actions:
                del actions['make_published']
        return actions


# ============================================
# 5. 自定义 Admin 站点
# ============================================

from django.contrib.admin import AdminSite


class MyAdminSite(AdminSite):
    """
    自定义 Admin 站点
    """
    site_header = '我的博客管理'
    site_title = '博客后台'
    index_title = '欢迎来到博客管理系统'
    
    def get_urls(self):
        """添加自定义 URL"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('my_view/', self.admin_view(self.my_view))
        ]
        return custom_urls + urls
    
    def my_view(self, request):
        """自定义视图"""
        from django.http import HttpResponse
        return HttpResponse('自定义管理视图')


admin_site = MyAdminSite(name='myadmin')


# ============================================
# 6. Inline 模型
# ============================================

class CommentInline(admin.TabularInline):
    """
    评论内联显示（表格形式）
    """
    model = Comment
    extra = 1
    readonly_fields = ['author', 'content', 'created_at']
    show_change_link = True


class CommentStackedInline(admin.StackedInline):
    """
    评论内联显示（堆叠形式）
    """
    model = Comment
    extra = 0
    fields = ['author', 'content', 'active']


@admin.register(Post)
class PostAdminWithInline(admin.ModelAdmin):
    list_display = ['title', 'author', 'status']
    inlines = [CommentInline]


# ============================================
# 7. 自定义 Admin 表单
# ============================================

from django import forms


class PostAdminForm(forms.ModelForm):
    """
    文章管理表单
    """
    class Meta:
        model = Post
        fields = '__all__'
        widgets = {
            'content': forms.Textarea(attrs={'rows': 20, 'cols': 80}),
        }
    
    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 5:
            raise forms.ValidationError('标题至少需要 5 个字符')
        return title


@admin.register(Post)
class PostAdminWithForm(admin.ModelAdmin):
    form = PostAdminForm


# ============================================
# 8. Admin 权限控制
# ============================================

@admin.register(Post)
class PostAdminWithPermissions(admin.ModelAdmin):
    list_display = ['title', 'author', 'status']
    
    def has_add_permission(self, request):
        """添加权限"""
        return request.user.has_perm('blog.add_post')
    
    def has_change_permission(self, request, obj=None):
        """修改权限"""
        if obj is None:
            return request.user.has_perm('blog.change_post')
        return obj.author == request.user or request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """删除权限"""
        if obj is None:
            return request.user.has_perm('blog.delete_post')
        return obj.author == request.user or request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        """查看权限"""
        return True
    
    def has_module_permission(self, request):
        """模块权限"""
        return request.user.is_authenticated


# ============================================
# 9. Admin 自定义模板
# ============================================
"""
自定义 Admin 模板：

目录结构：
templates/
└── admin/
    ├── base_site.html          # 基础模板
    ├── index.html              # 首页
    ├── change_form.html        # 编辑表单
    ├── change_list.html        # 列表页
    └── blog/
        └── post/
            ├── change_form.html    # 文章编辑
            └── change_list.html    # 文章列表

templates/admin/base_site.html:
{% extends "admin/base_site.html" %}

{% block title %}{{ title }} | 我的博客管理{% endblock %}

{% block branding %}
<h1 id="site-name">
    <a href="{% url 'admin:index' %}">
        🌸 我的博客管理
    </a>
</h1>
{% endblock %}

{% block nav-global %}
<div class="nav-global">
    <a href="/" target="_blank">查看网站</a>
</div>
{% endblock %}
"""

# ============================================
# 10. Admin CSS 样式自定义
# ============================================
"""
# settings.py

class Media:
    css = {
        'all': ('css/admin.css',)
    }
    js = ('js/admin.js',)


# static/css/admin.css

/* 自定义 Admin 样式 */
.field-title {
    font-weight: bold;
}

.status-published {
    color: green;
}

.status-draft {
    color: orange;
}

/* 自定义列表样式 */
.model-post.change-list .field-views {
    text-align: right;
}
"""

# ============================================
# 11. 第三方 Admin 扩展
# ============================================
"""
推荐第三方 Admin 扩展：

1. django-grappelli
   pip install django-grappelli
   
   # settings.py
   INSTALLED_APPS = [
       'grappelli',
       ...
   ]
   
   # urls.py
   path('grappelli/', include('grappelli.urls')),

2. django-jazzmin
   pip install django-jazzmin
   
   # settings.py
   INSTALLED_APPS = [
       'jazzmin',
       ...
   ]

3. django-simpleui
   pip install django-simpleui
   
   # settings.py
   INSTALLED_APPS = [
       'simpleui',
       ...
   ]

4. django-import-export
   pip install django-import-export
   
   from import_export.admin import ImportExportModelAdmin
   
   @admin.register(Post)
   class PostAdmin(ImportExportModelAdmin):
       list_display = ['title', 'author', 'status']

5. django-admin-rangefilter
   pip install django-admin-rangefilter
   
   from rangefilter.filters import DateRangeFilter
   
   @admin.register(Post)
   class PostAdmin(admin.ModelAdmin):
       list_filter = [
           ('publish', DateRangeFilter),
       ]
"""

# ============================================
# 12. 创建超级用户
# ============================================
"""
# 命令行创建超级用户
python manage.py createsuperuser

# 或使用脚本
from django.contrib.auth.models import User

User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='admin123'
)
"""

# ============================================
# 练习任务
# ============================================
"""
1. 为你的模型创建 Admin 配置

2. 自定义列表显示：
   - list_display
   - list_filter
   - search_fields

3. 创建自定义 Admin 动作：
   - 批量发布文章
   - 批量删除

4. 使用 Inline 显示关联模型

5. 安装并配置第三方 Admin 主题
"""

if __name__ == "__main__":
    print("亲爱的主人，这是 Django Admin 管理后台的学习笔记~ 🌸")
    print("请按照上面的步骤学习 Admin 后台！")
    print("\n关键命令：")
    print("  python manage.py createsuperuser")
    print("  访问 http://127.0.0.1:8000/admin/")
