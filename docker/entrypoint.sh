#!/bin/sh
set -e

echo "Running migrations..."
python manage.py migrate --noinput

if [ "${SEED_ON_START}" = "1" ]; then
  echo "Seeding initial data..."
  python manage.py seed_initial --admin-email="${ADMIN_EMAIL:-admin@example.com}" --admin-password="${ADMIN_PASSWORD:-admin12345}"
fi

echo "Starting gunicorn..."
gunicorn capacitaciones.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120
