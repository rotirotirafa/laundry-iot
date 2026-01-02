#!/bin/sh
set -e

# Wait until Postgres is available
echo "Waiting for database..."
while :
do
  python - <<PYCODE
import os
import sys
try:
    import psycopg2
    conn = psycopg2.connect(dbname=os.environ.get('DB_NAME'), user=os.environ.get('DB_USER'), password=os.environ.get('DB_PASS'), host=os.environ.get('DB_HOST'), port=os.environ.get('DB_PORT'))
    conn.close()
except Exception as e:
    sys.exit(1)
sys.exit(0)
PYCODE
  if [ $? -eq 0 ]; then
    break
  fi
  echo "Postgres is unavailable - sleeping"
  sleep 2
done

echo "Database is ready!"

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Migrate django-q tables
echo "Setting up django-q..."
python manage.py migrate django_q --noinput || true

# Setup scheduler
echo "Configuring scheduler..."
python manage.py setup_scheduler || true

# Create superuser if variables are provided
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "Creating superuser..."
  python manage.py shell <<PYEOF
import os
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created successfully!")
else:
    print(f"Superuser '{username}' already exists.")
PYEOF
fi

# Collect static files (if needed)
python manage.py collectstatic --noinput || true

echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000
