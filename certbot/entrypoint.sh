#!/bin/sh
chmod 600 /config/cloudflare.ini
python certbot/auto_cert.py