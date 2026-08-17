#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn setup.wsgi:application \
    --bind 0.0.0.0:8005 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
