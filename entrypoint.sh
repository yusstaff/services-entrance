#!/bin/sh

cd /app/backend
# Check if /config/gunicorn.pid exists and if the PID is running. If yes, delete the file.
if [ -f "/config/gunicorn.pid" ]; then
    pid=$(cat /config/gunicorn.pid)
    if ps -p "$pid" > /dev/null 2>&1; then
        echo "/config/gunicorn.pid is occupied by PID $pid. Deleting file."
    else
        echo "/config/gunicorn.pid is a stale file. Deleting file."
    fi
    rm /config/gunicorn.pid
fi
gunicorn -w 1 app:app -b 0.0.0.0:5571 --daemon --pid /config/gunicorn.pid --access-logfile /app/log/flask.log --error-logfile /app/log/flask.log

touch /app/log/quasar.log
nohup quasar serve -H 0.0.0.0 -p 5572 /app/frontend/dist/spa/ > /app/log/quasar.log 2>&1 &

echo 1 > /config/envoy-restart-epoch.txt
touch /app/log/envoy.log
if [ ! -e "/config/envoy.yaml" ]; then
    cp /config/envoy-template.yaml /config/envoy.yaml
fi
nohup envoy -c /config/envoy.yaml --base-id 0 --restart-epoch 0 > /app/log/envoy.log 2>&1 &
