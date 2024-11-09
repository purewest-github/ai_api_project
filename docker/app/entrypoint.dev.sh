#!/bin/sh

set -e

# ログディレクトリの確認
mkdir -p /var/log/django
chmod 777 /var/log/django

# マイグレーションディレクトリの初期化
mkdir -p ai_api_app/migrations
touch ai_api_app/migrations/__init__.py

# データベースの接続を待機
echo "Waiting for database..."
while ! nc -z db 3306; do
    echo "Waiting for database connection..."
    sleep 1
done
echo "Database started"

# データベースが実際に準備できるまで少し待機
sleep 5

# マイグレーションを作成して適用
python manage.py makemigrations ai_api_app
python manage.py migrate

# Tailwind CSSのウォッチを開始（バックグラウンドで実行）
npm run watch &

# Django開発サーバーを起動
exec "$@"