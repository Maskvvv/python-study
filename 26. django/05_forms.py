"""
Django 学习笔记 05 - 表单处理
=====================================

亲爱的主人，让我们学习 Django 的表单处理系统！📝
"""

# ============================================
# 1. Django 表单概述
# ============================================
"""
Django 表单系统提供：
    ✅ 表单字段定义和验证
    ✅ 自动生成 HTML 表单
    ✅ CSRF 保护
    ✅ 错误信息显示
    ✅ 数据清洗和转换
"""

# ============================================
# 2. 创建表单类
# ============================================

# blog/forms.py

from django import forms
from .models import Post, Comment, Category


class ContactForm(forms.Form):
    """
    联系表单 - 基础表单示例
    """
    name = forms.CharField(
        label='姓名',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入您的姓名'
        })
    )
    email = forms.EmailField(
        label='邮箱',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入您的邮箱'
        })
    )
    subject = forms.CharField(
        label='主题',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入主题'
        })
    )
    message = forms.CharField(
        label='消息内容',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': '请输入您的消息...'
        })
    )
    
    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 2:
            raise forms.ValidationError('姓名至少需要 2 个字符')
        return name
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if 'spam' in email:
            raise forms.ValidationError('请不要使用垃圾邮箱')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        email = cleaned_data.get('email')
        
        if name and email:
            if name.lower() in email.lower():
                raise forms.ValidationError('姓名不应该包含在邮箱中')
        
        return cleaned_data


class PostForm(forms.ModelForm):
    """
    文章表单 - 模型表单示例
    """
    class Meta:
        model = Post
        fields = ['title', 'slug', 'category', 'tags', 'content', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入文章标题'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL 别名（自动生成）'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tags': forms.CheckboxSelectMultiple(),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': '请输入文章内容...'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        help_texts = {
            'title': '文章标题应该简洁明了',
            'slug': 'URL 友好的标识符，留空则自动生成',
        }
        error_messages = {
            'title': {
                'required': '请输入文章标题',
                'max_length': '标题太长了',
            },
        }
    
    def clean_slug(self):
        slug = self.cleaned_data['slug']
        if not slug:
            from django.utils.text import slugify
            slug = slugify(self.cleaned_data['title'])
        return slug
    
    def save(self, commit=True):
        post = super().save(commit=False)
        if commit:
            post.save()
            self.save_m2m()
        return post


class CommentForm(forms.ModelForm):
    """
    评论表单
    """
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '写下你的评论...'
            })
        }
        labels = {
            'content': '评论内容'
        }


class SearchForm(forms.Form):
    """
    搜索表单
    """
    query = forms.CharField(
        label='搜索',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '搜索文章...',
            'type': 'search'
        })
    )
    category = forms.ModelChoiceField(
        label='分类',
        queryset=Category.objects.all(),
        required=False,
        empty_label='全部分类',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    order_by = forms.ChoiceField(
        label='排序',
        choices=[
            ('-publish', '最新发布'),
            ('-views', '最多浏览'),
            ('-likes', '最多点赞'),
            ('title', '标题排序'),
        ],
        required=False,
        initial='-publish',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )


# ============================================
# 3. 表单字段类型
# ============================================
"""
常用字段类型：

文本字段：
    - CharField: 字符串字段
    - EmailField: 邮箱字段
    - URLField: URL 字段
    - RegexField: 正则表达式字段
    - SlugField: Slug 字段

数值字段：
    - IntegerField: 整数字段
    - FloatField: 浮点数字段
    - DecimalField: 十进制字段

布尔字段：
    - BooleanField: 布尔字段
    - NullBooleanField: 可为空的布尔字段

选择字段：
    - ChoiceField: 选择字段
    - TypedChoiceField: 类型化选择字段
    - MultipleChoiceField: 多选字段

日期时间字段：
    - DateField: 日期字段
    - TimeField: 时间字段
    - DateTimeField: 日期时间字段

文件字段：
    - FileField: 文件字段
    - ImageField: 图片字段

其他字段：
    - GenericIPAddressField: IP 地址字段
    - UUIDField: UUID 字段
    - JSONField: JSON 字段
"""

# ============================================
# 4. 表单字段参数
# ============================================
"""
通用参数：
    - required: 是否必填（默认 True）
    - label: 字段标签
    - initial: 初始值
    - widget: 控件
    - help_text: 帮助文本
    - error_messages: 错误消息
    - validators: 验证器列表
    - disabled: 是否禁用
    
字符串字段特有：
    - max_length: 最大长度
    - min_length: 最小长度
    
数值字段特有：
    - max_value: 最大值
    - min_value: 最小值
"""

# ============================================
# 5. 表单控件（Widget）
# ============================================

class AdvancedForm(forms.Form):
    """
    高级表单控件示例
    """
    text_input = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    hidden = forms.CharField(
        widget=forms.HiddenInput()
    )
    
    textarea = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
    )
    
    checkbox = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    select = forms.ChoiceField(
        choices=[
            ('option1', '选项 1'),
            ('option2', '选项 2'),
            ('option3', '选项 3'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    radio = forms.ChoiceField(
        choices=[
            ('option1', '选项 1'),
            ('option2', '选项 2'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )


# ============================================
# 6. 表单验证
# ============================================

class RegistrationForm(forms.Form):
    """
    用户注册表单 - 验证示例
    """
    username = forms.CharField(
        label='用户名',
        min_length=4,
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='邮箱',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='密码',
        min_length=8,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password_confirm = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    def clean_username(self):
        username = self.cleaned_data['username']
        from django.contrib.auth.models import User
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('该用户名已被使用')
        if not username.isalnum():
            raise forms.ValidationError('用户名只能包含字母和数字')
        return username
    
    def clean_email(self):
        email = self.cleaned_data['email']
        from django.contrib.auth.models import User
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已被注册')
        return email
    
    def clean_password(self):
        password = self.cleaned_data['password']
        if password.isdigit():
            raise forms.ValidationError('密码不能全是数字')
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError('两次输入的密码不一致')
        
        return cleaned_data


# ============================================
# 7. 视图中处理表单
# ============================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models


def contact_view(request):
    """
    联系表单视图
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            from django.core.mail import send_mail
            send_mail(
                subject=f'来自 {name} 的消息：{subject}',
                message=f'发件人：{email}\n\n{message}',
                from_email=email,
                recipient_list=['admin@example.com'],
            )
            
            messages.success(request, '消息发送成功！我们会尽快回复您~ 💖')
            return redirect('contact')
    else:
        form = ContactForm()
    
    return render(request, 'blog/contact.html', {'form': form})


@login_required
def post_create(request):
    """
    创建文章
    """
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            messages.success(request, '文章创建成功！✨')
            return redirect(post.get_absolute_url())
    else:
        form = PostForm()
    
    return render(request, 'blog/post_form.html', {
        'form': form,
        'title': '创建文章'
    })


@login_required
def post_update(request, pk):
    """
    更新文章
    """
    post = get_object_or_404(Post, pk=pk, author=request.user)
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save()
            messages.success(request, '文章更新成功！✨')
            return redirect(post.get_absolute_url())
    else:
        form = PostForm(instance=post)
    
    return render(request, 'blog/post_form.html', {
        'form': form,
        'title': '编辑文章',
        'post': post
    })


@login_required
def post_delete(request, pk):
    """
    删除文章
    """
    post = get_object_or_404(Post, pk=pk, author=request.user)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, '文章已删除！')
        return redirect('blog:post_list')
    
    return render(request, 'blog/post_confirm_delete.html', {'post': post})


@login_required
def comment_add(request, post_id):
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
            messages.success(request, '评论发表成功！💬')
    
    return redirect(post.get_absolute_url())


def post_search(request):
    """
    文章搜索
    """
    form = SearchForm(request.GET)
    posts = Post.objects.filter(status='published')
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        order_by = form.cleaned_data.get('order_by', '-publish')
        
        if query:
            posts = posts.filter(
                models.Q(title__icontains=query) |
                models.Q(content__icontains=query)
            )
        
        if category:
            posts = posts.filter(category=category)
        
        posts = posts.order_by(order_by)
    
    return render(request, 'blog/post_search.html', {
        'form': form,
        'posts': posts
    })


# ============================================
# 8. 表单模板示例
# ============================================
"""
templates/blog/contact.html:

{% extends 'base.html' %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-6">
        <h1 class="mb-4">📬 联系我们</h1>
        
        <form method="post" novalidate>
            {% csrf_token %}
            
            {% if form.non_field_errors %}
            <div class="alert alert-danger">
                {% for error in form.non_field_errors %}
                    <p>{{ error }}</p>
                {% endfor %}
            </div>
            {% endif %}
            
            {% for field in form %}
            <div class="mb-3">
                <label for="{{ field.id_for_label }}" class="form-label">
                    {{ field.label }}
                    {% if field.field.required %}<span class="text-danger">*</span>{% endif %}
                </label>
                {{ field }}
                
                {% if field.help_text %}
                <div class="form-text">{{ field.help_text }}</div>
                {% endif %}
                
                {% for error in field.errors %}
                <div class="text-danger small">{{ error }}</div>
                {% endfor %}
            </div>
            {% endfor %}
            
            <button type="submit" class="btn btn-primary">
                发送消息 ✉️
            </button>
        </form>
    </div>
</div>
{% endblock %}
"""

# ============================================
# 9. 文件上传
# ============================================

class UploadForm(forms.Form):
    """
    文件上传表单
    """
    title = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )


def upload_view(request):
    """
    文件上传视图
    """
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data['title']
            uploaded_file = form.cleaned_data['file']
            uploaded_image = form.cleaned_data.get('image')
            
            # 处理文件
            with open(f'media/{uploaded_file.name}', 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            messages.success(request, '文件上传成功！📁')
            return redirect('upload')
    else:
        form = UploadForm()
    
    return render(request, 'blog/upload.html', {'form': form})


# ============================================
# 10. FormSet - 表单集
# ============================================

from django.forms import formset_factory

class ItemForm(forms.Form):
    """
    项目表单
    """
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '项目名称'})
    )
    quantity = forms.IntegerField(
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    price = forms.DecimalField(
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )


def formset_view(request):
    """
    表单集视图
    """
    ItemFormSet = formset_factory(ItemForm, extra=3, can_delete=True)
    
    if request.method == 'POST':
        formset = ItemFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                    name = form.cleaned_data['name']
                    quantity = form.cleaned_data['quantity']
                    price = form.cleaned_data['price']
                    print(f'{name}: {quantity} x {price}')
            
            messages.success(request, '数据保存成功！')
            return redirect('formset')
    else:
        formset = ItemFormSet()
    
    return render(request, 'blog/formset.html', {'formset': formset})


# ============================================
# 练习任务
# ============================================
"""
1. 创建一个联系表单，包含姓名、邮箱、主题和消息字段

2. 创建一个文章表单，使用 ModelForm

3. 实现表单验证：
   - 字段级验证
   - 表单级验证

4. 创建文件上传表单，支持图片上传

5. 使用 FormSet 创建多个项目的表单
"""

if __name__ == "__main__":
    print("亲爱的主人，这是 Django 表单处理的学习笔记~ 🌸")
    print("请按照上面的步骤学习表单处理！")
    print("\n关键概念：")
    print("  - Form 类：定义表单字段")
    print("  - ModelForm：基于模型创建表单")
    print("  - 表单验证：clean_<field>() 和 clean()")
    print("  - Widget：表单控件")
