#!/bin/bash
SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-"admin@test.com"}
SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD:-"1234"}
cd /app/

/opt/venv/bin/python manage.py collectstatic --noinput
/opt/venv/bin/python manage.py migrate --noinput
/opt/venv/bin/python manage.py createsuperuser --email $SUPERUSER_EMAIL --password $SUPERUSER_PASSWORD --noinput || true