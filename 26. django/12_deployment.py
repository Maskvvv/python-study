"""
Django 学习笔记 12 - 部署
=====================================

亲爱的主人，让我们学习 Django 应用的部署！🚀
"""

# ============================================
# 1. 部署前准备
# ============================================
"""
部署前检查清单：
    ✅ DEBUG = False
    ✅ SECRET_KEY 安全
    ✅ ALLOWED_HOSTS 配置
    ✅ 静态文件收集
    ✅ 数据库配置
    ✅ HTTPS 配置
    ✅ 安全设置
"""

# ============================================
# 2. 生产环境配置
# ============================================
"""
# settings/production.py

import os
from .base import *

DEBUG = False

# 从环境变量读取
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = [
    'yourdomain.com',
    'www.yourdomain.com',
]

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# 安全设置
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 31536000
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# 静态文件
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/error.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# 缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
    }
}

# 邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
"""

# ============================================
# 3. 使用 Gunicorn
# ============================================
"""
# 安装 Gunicorn
pip install gunicorn

# 运行 Gunicorn
gunicorn myproject.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --threads 2 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -

# gunicorn.conf.py
import multiprocessing

bind = '0.0.0.0:8000'
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2
timeout = 60
keepalive = 120
errorlog = '/var/log/gunicorn/error.log'
accesslog = '/var/log/gunicorn/access.log'
loglevel = 'info'
"""

# ============================================
# 4. 使用 uWSGI
# ============================================
"""
# 安装 uWSGI
pip install uwsgi

# uwsgi.ini
[uwsgi]
project = myproject
base = /var/www

chdir = %(base)/%(project)
home = %(base)/%(project)/venv
module = %(project).wsgi:application

master = true
processes = 5
threads = 2

socket = %(base)/%(project)/%(project).sock
chmod-socket = 666
vacuum = true

die-on-term = true
max-requests = 5000
harakiri = 60

logto = /var/log/uwsgi/%(project).log

# 运行 uWSGI
uwsgi --ini uwsgi.ini
"""

# ============================================
# 5. Nginx 配置
# ============================================
"""
# /etc/nginx/sites-available/myproject

upstream myproject {
    server unix:///var/www/myproject/myproject.sock;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location /static/ {
        alias /var/www/myproject/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /var/www/myproject/media/;
        expires 30d;
    }

    location / {
        include uwsgi_params;
        uwsgi_pass myproject;
        uwsgi_read_timeout 60;
        uwsgi_connect_timeout 60;
    }

    access_log /var/log/nginx/myproject_access.log;
    error_log /var/log/nginx/myproject_error.log;
}

# 启用站点
sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
"""

# ============================================
# 6. 使用 Supervisor
# ============================================
"""
# 安装 Supervisor
sudo apt-get install supervisor

# /etc/supervisor/conf.d/myproject.conf

[program:myproject]
command=/var/www/myproject/venv/bin/gunicorn \
    --bind unix:/var/www/myproject/myproject.sock \
    --workers 4 \
    --threads 2 \
    myproject.wsgi:application
directory=/var/www/myproject
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/myproject.log
environment=DJANGO_SETTINGS_MODULE="myproject.settings.production"

# 重启 Supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart myproject
"""

# ============================================
# 7. 使用 Systemd
# ============================================
"""
# /etc/systemd/system/gunicorn.service

[Unit]
Description=Gunicorn daemon for Django
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/myproject
Environment="DJANGO_SETTINGS_MODULE=myproject.settings.production"
ExecStart=/var/www/myproject/venv/bin/gunicorn \
    --workers 4 \
    --threads 2 \
    --bind unix:/var/www/myproject/myproject.sock \
    myproject.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target

# 启动服务
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
"""

# ============================================
# 8. Docker 部署
# ============================================

# Dockerfile
DOCKERFILE = """
# 使用 Python 基础镜像
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 暴露端口
EXPOSE 8000

# 运行 Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myproject.wsgi:application"]
"""

# docker-compose.yml
DOCKER_COMPOSE = """
version: '3.8'

services:
  web:
    build: .
    command: gunicorn myproject.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    expose:
      - 8000
    environment:
      - DEBUG=0
      - DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
      - DATABASE_URL=postgres://postgres:postgres@db:5432/myproject
      - REDIS_URL=redis://redis:6379/1
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=myproject
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - web

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
"""

# ============================================
# 9. 部署到云平台
# ============================================
"""
# Heroku 部署

# Procfile
web: gunicorn myproject.wsgi:application
release: python manage.py migrate

# requirements.txt
gunicorn
django-heroku
whitenoise

# settings.py
import django_heroku
django_heroku.settings(locals())

# 部署命令
heroku create myapp
heroku config:set DJANGO_SECRET_KEY=your-secret-key
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser


# AWS 部署（使用 Elastic Beanstalk）

# .ebextensions/django.config
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: myproject.wsgi:application
  aws:elasticbeanstalk:application:environment:
    DJANGO_SETTINGS_MODULE: myproject.settings.production

# 部署命令
eb init -p python-3.11 myapp
eb create production
eb deploy


# DigitalOcean App Platform

# app.yaml
name: myproject
services:
- name: web
  github:
    repo: username/myproject
    branch: main
  run_command: gunicorn myproject.wsgi:application
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  env:
  - key: DJANGO_SECRET_KEY
    value: your-secret-key
  - key: DEBUG
    value: "False"
"""

# ============================================
# 10. CI/CD 配置
# ============================================
"""
# .github/workflows/deploy.yml

name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python manage.py test
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/test
    
    - name: Deploy to production
      if: success()
      run: |
        # 部署脚本
"""

# ============================================
# 11. 部署脚本
# ============================================
"""
#!/bin/bash
# deploy.sh

set -e

echo "开始部署..."

# 拉取最新代码
git pull origin main

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 收集静态文件
python manage.py collectstatic --noinput

# 数据库迁移
python manage.py migrate

# 清除缓存
python manage.py clear_cache

# 重启服务
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "部署完成！"
"""

# ============================================
# 12. 监控和日志
# ============================================
"""
# 使用 Sentry 错误监控
# pip install sentry-sdk

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    environment='production',
)

# 使用 Prometheus 监控
# pip install django-prometheus

INSTALLED_APPS = [
    'django_prometheus',
    ...
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    ...
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

# urls.py
urlpatterns = [
    path('metrics/', include('django_prometheus.urls')),
]
"""

# ============================================
# 13. 安全检查清单
# ============================================
"""
# 运行安全检查
python manage.py check --deploy

安全检查项：
    ✅ DEBUG = False
    ✅ SECRET_KEY 安全且不泄露
    ✅ ALLOWED_HOSTS 正确配置
    ✅ SECURE_SSL_REDIRECT = True
    ✅ SESSION_COOKIE_SECURE = True
    ✅ CSRF_COOKIE_SECURE = True
    ✅ SECURE_HSTS_SECONDS 设置
    ✅ SECURE_CONTENT_TYPE_NOSNIFF = True
    ✅ SECURE_BROWSER_XSS_FILTER = True
    ✅ X_FRAME_OPTIONS = 'DENY'
    ✅ 数据库密码安全
    ✅ 文件上传安全
    ✅ 用户输入验证
"""

# ============================================
# 练习任务
# ============================================
"""
1. 配置生产环境设置：
   - 创建 settings/production.py
   - 使用环境变量
   - 配置安全设置

2. 使用 Gunicorn 部署：
   - 安装和配置 Gunicorn
   - 配置 Nginx 反向代理

3. 使用 Docker 部署：
   - 编写 Dockerfile
   - 编写 docker-compose.yml
   - 配置多容器应用

4. 配置 CI/CD：
   - 使用 GitHub Actions
   - 自动化测试和部署

5. 配置监控：
   - 使用 Sentry 错误监控
   - 使用 Prometheus 性能监控
"""

if __name__ == "__main__":
    print("亲爱的主人，这是 Django 部署的学习笔记~ 🌸")
    print("请按照上面的步骤学习部署！")
    print("\n关键命令：")
    print("  python manage.py check --deploy")
    print("  python manage.py collectstatic")
    print("  gunicorn myproject.wsgi:application")
