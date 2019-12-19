#!/bin/bash
echo "Step 03."
cd $APP_PATH/

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3
