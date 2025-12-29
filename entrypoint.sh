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

# Run migrations and start server
python manage.py migrate --noinput
python manage.py collectstatic --noinput || true
exec python manage.py runserver 0.0.0.0:8000
