#!/bin/sh

# コンテナを停止し、ボリュームも削除
docker compose -f docker-compose.dev.yml down -v

# コンテナを起動
docker compose -f docker-compose.dev.yml up -d

# データベースの準備ができるまで待機
echo "Waiting for containers to be ready..."
sleep 20  # 待機時間を増やす

# データベースをリセット（-pオプションを修正）
docker compose -f docker-compose.dev.yml exec db mysql -uroot -proot -e "
DROP DATABASE IF EXISTS AI_API_DB;
CREATE DATABASE AI_API_DB;
GRANT ALL PRIVILEGES ON AI_API_DB.* TO 'Django_Developer_User'@'%';
FLUSH PRIVILEGES;
"

# マイグレーションの作成と適用
docker compose -f docker-compose.dev.yml exec app python manage.py makemigrations ai_api_app
docker compose -f docker-compose.dev.yml exec app python manage.py migrate

# 静的ファイルの収集
docker compose -f docker-compose.dev.yml exec app python manage.py collectstatic --noinput --clear

# スーパーユーザーの作成
docker compose -f docker-compose.dev.yml exec app python manage.py createsuperuser