#!/bin/bash
APP_PORT=${PORT:-8000}
cd /app/

/opt/venv/bin/gunicorn --worker-tmp-dir /dev/shm -k uvicorn.workers.UvicornWorker yourfan.wsgi:application --bind "0.0.0.0:${APP_PORT}"
