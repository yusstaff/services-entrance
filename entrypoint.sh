#!/bin/sh

cd /app/backend
gunicorn -w 1 app:app -b 0.0.0.0:5571 --daemon --pid /config/gunicorn.pid --access-logfile /app/log/flask.log --error-logfile /app/log/flask.log

touch /app/log/quasar.log
nohup quasar serve -H 0.0.0.0 -p 5572 /app/frontend/dist/spa/ > /app/log/quasar.log 2>&1 &

echo 1 > /config/envoy-restart-epoch.txt
touch /app/log/envoy.log
if [ ! -e "/config/envoy.yaml" ]; then
    cp /config/envoy-template.yaml /config/envoy.yaml
fi
nohup envoy -c /config/envoy.yaml --base-id 0 --restart-epoch 0 > /app/log/envoy.log 2>&1 &
