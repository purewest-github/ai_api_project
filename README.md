# ai_api_project
ClaudeとChatGPTのハイブリッドAPI

![Python](https://img.shields.io/badge/python-3.12-blue)
![Django](https://img.shields.io/badge/django-4.2-blue)
![MySQL](https://img.shields.io/badge/mysql-8.0-blue)
![Nginx](https://img.shields.io/badge/nginx-1.25-blue)
![uWSGI](https://img.shields.io/badge/uwsgi-2.0.23-blue)


このプロジェクトは、Dockerを使用してコンテナ化されたDjangoアプリケーション、リバースプロキシとしてのNginx、そしてデータベースとしてMySQLをセットアップします。

## 開発環境のセットアップ

1. ルートディレクトリに`.env.dev`ファイルを作成し、以下の内容を記入してください：
```
MYSQL_ROOT_PASSWORD=rootパスワード
MYSQL_DATABASE=データベース名
# init.sqlのユーザー名と同じにすること
MYSQL_USER=ユーザー名
MYSQL_PASSWORD=パスワード
DJANGO_SECRET_KEY=Djangoのシークレットキー
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]
```

2. 開発環境をビルドして実行します：

2-1. Djangoのプロジェクト構成を作成する。
```
docker compose -f docker-compose.dev.yml run app django-admin startproject <プロジェクト名> .
```

2-1-2. <プロジェクト名>/settings.pyを設定する
```
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost 127.0.0.1 [::1]').split()

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = '<プロジェクト名>.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
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

WSGI_APPLICATION = '<プロジェクト名>.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'mysql.connector.django',
        'NAME': os.environ.get('MYSQL_DATABASE'),
        'USER': os.environ.get('MYSQL_USER'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD'),
        'HOST': 'db',
        'PORT': '3306',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 追加の静的ファイルディレクトリ
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

2-2. Djangoアプリ構成を作成する。
```
docker compose -f docker-compose.dev.yml run app python manage.py startapp <アプリ名>
```

2-2-2. <プロジェクト名>/settings.pyにアプリを追加する。
```
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost 127.0.0.1 [::1]').split()

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    '<アプリ名>',  # 追加したアプリケーション
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = '<プロジェクト名>.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
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

WSGI_APPLICATION = '<プロジェクト名>.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'mysql.connector.django',
        'NAME': os.environ.get('MYSQL_DATABASE'),
        'USER': os.environ.get('MYSQL_USER'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD'),
        'HOST': 'db',
        'PORT': '3306',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 追加の静的ファイルディレクトリ
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

Dockerを起動する。
```
docker compose -f docker-compose.dev.yml up -d --build
```

3. `http://localhost:8000` でアプリケーションにアクセスできます。

## 本番環境のセットアップ

1. 本番環境用の`.env.prod`ファイルを作成し、以下のような環境変数を設定します：
```
MYSQL_ROOT_PASSWORD=本番用rootパスワード
MYSQL_DATABASE=
# init.sqlのユーザー名と同じにすること
MYSQL_USER=本番用ユーザー名
MYSQL_PASSWORD=本番用パスワード
DJANGO_SECRET_KEY=本番用Djangoシークレットキー
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=あなたのドメイン.com
```

2. 本番環境をビルドして実行します：
```
docker-compose -f docker-compose.prod.yml up --build
```

3. `http://localhost` またはあなたのドメインでアプリケーションにアクセスできます。

## その他のコマンド

- マイグレーションの作成：
```
docker-compose exec app python manage.py makemigrations
```

- マイグレーションの適用：
```
docker-compose exec app python manage.py migrate
```

- スーパーユーザーの作成：
```
docker-compose exec app python manage.py createsuperuser
```

## デプロイメント

このセットアップは、AWS ECS Fargateに簡単にデプロイできるように設計されています。以下の点に注意してください：

1. DockerイメージをAmazon ECRにプッシュします。
2. ECSタスク定義とサービスをセットアップします。
3. ECSで環境変数を設定します。
4. FargateサービスのApplication Load Balancerをセットアップします。

AWS ECS Fargateへの詳細なデプロイ手順については、AWSのドキュメントを参照してください。

## プロジェクト構造
```
.
├── .dockerignore
├── .gitignore
├── docker-compose.yml
├── docker-compose.prod.yml
├── README.md
├── app
│   ├── manage.py
│   ├── core
│   │   ├── init.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── static
│   │   └── .gitkeep
│   └── requirements.txt
└── docker
├── app
│   ├── Dockerfile.dev
│   ├── Dockerfile.prod
│   └── uwsgi.ini
├── mysql
│   ├── Dockerfile
│   ├── init.sql
│   └── my.cnf
└── nginx
├── Dockerfile
└── nginx.conf
```

## 使用技術

- Django 4.2.7
- MySQL 8.0
- Nginx 1.25
- uWSGI 2.0.23
- Docker & Docker Compose

## 貢献

プロジェクトへの貢献方法や行動規範については、CONTRIBUTING.mdをお読みください。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細はLICENSE.mdファイルをご覧ください。