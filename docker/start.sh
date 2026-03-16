#!/usr/bin/env bash
set -euo pipefail
umask 027

mkdir -p /config/compose /var/www/client_body_temp /var/www/proxy_temp

echo "Replacing env constants in frontend assets"
for file in /app/js/app.*.js* /app/index.html; do
  [ -e "$file" ] || continue
  sed -i "s|VUE_APP_THEME|${THEME:-Default}|g" "$file"
  sed -i "s|VUE_APP_LOGO|${LOGO:-}|g" "$file"
done

echo "Starting Yacht backend and frontend"
uvicorn --uds /tmp/gunicorn.sock api.main:app &
uvicorn_pid=$!

nginx -c /etc/nginx/nginx.conf -g "daemon off;" &
nginx_pid=$!

wait -n "$uvicorn_pid" "$nginx_pid"
exit_code=$?
kill "$uvicorn_pid" "$nginx_pid" 2>/dev/null || true
wait || true
exit "$exit_code"
