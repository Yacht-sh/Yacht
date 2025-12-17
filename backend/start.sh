#!/bin/sh
set -e

# Start Nginx
echo "Starting Nginx..."
nginx

# Start Backend
# Determine if we should run with Uvicorn (dev) or Gunicorn (prod)
# For now, we follow the nginx.conf expectation: upstream unix:/tmp/gunicorn.sock
# So we must use Gunicorn binding to that socket.

echo "Starting Gunicorn..."
# Ensure /tmp exists (it should)
# Run Gunicorn binding to unix socket and also maybe TCP for debugging?
# nginx.conf says: upstream api_server { server unix:/tmp/gunicorn.sock fail_timeout=0; }
# So we bind to unix:/tmp/gunicorn.sock

# We need to find where the app object is. It is in api.main:app
# We are in /api directory (based on Dockerfile WORKDIR)

# Note: The original Dockerfile had CMD ["python3", "app.py"] which was wrong.
# The original nginx.conf expects a unix socket at /tmp/gunicorn.sock.

exec gunicorn api.main:app \
    --workers 1 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind unix:/tmp/gunicorn.sock \
    --bind 0.0.0.0:8000 \
    --log-level info
