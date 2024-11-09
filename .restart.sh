#!/bin/sh

# エラーが発生したら即座に停止
set -e

echo "Stopping containers and cleaning up..."
docker compose -f docker-compose.dev.yml down --rmi all --volumes --remove-orphans

echo "Cleaning Docker system..."
docker system prune -af

echo "Removing local directories..."
rm -rf app/staticfiles app/logs app/static
rm -rf app/ai_api_app/migrations/__pycache__
rm -rf app/ai_api_app/migrations/[0-9]*.py

# マイグレーションディレクトリの初期化
echo "Initializing migrations directory..."
mkdir -p app/ai_api_app/migrations
touch app/ai_api_app/migrations/__init__.py

echo "Starting containers..."
docker compose -f docker-compose.dev.yml up -d

echo "Waiting for containers to be ready..."
sleep 20

echo "Checking logs..."
docker logs Django

echo "Collecting static files..."
docker compose -f docker-compose.dev.yml exec -T app python manage.py collectstatic --noinput --clear

echo "Creating superuser..."
docker compose -f docker-compose.dev.yml exec app python manage.py createsuperuser

echo "Final container status:"
docker ps -a

echo "Setup completed successfully!"