#!/usr/bin/env bash

set -e

echo "Starting Django application..."
python manage.py collectstatic --no-input
# python manage.py migrate --fake-initial

echo "Starting uWSGI server..."
ls -la /opt/app/uwsgi/uwsgi.ini
uwsgi --strict --ini /opt/app/uwsgi/uwsgi.ini