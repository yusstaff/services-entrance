# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.245.2/containers/python-3/.devcontainer/base.Dockerfile

# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.10, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.10-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.10-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
FROM linuxserver/wireguard:1.0.20210914-legacy

RUN apt update && apt install -y debian-keyring debian-archive-keyring apt-transport-https curl lsb-release
RUN curl -sL 'https://deb.dl.getenvoy.io/public/gpg.8115BA8E629CC074.key' | gpg --dearmor -o /usr/share/keyrings/getenvoy-keyring.gpg
RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/getenvoy-keyring.gpg] https://deb.dl.getenvoy.io/public/deb/ubuntu $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/getenvoy.list
RUN apt update && apt install -y getenvoy-envoy

RUN apt update && apt install -y python3 python3-pip

RUN apt update && apt install -y dnsutils

RUN pip install flask flask-cors gunicorn

RUN pip install PyYAML flake8

RUN pip install flask-jwt-extended Werkzeug

RUN curl -fsSL https://deb.nodesource.com/setup_current.x | bash - && \
    apt-get install -y nodejs

RUN npm install -g @quasar/cli serve

WORKDIR /app/self-signed
RUN openssl genpkey -algorithm RSA -out private.key -pkeyopt rsa_keygen_bits:2048
RUN openssl req -new -x509 -key private.key -out certificate.crt -days 36500 -subj "/CN=*.servicesentrance.com"

WORKDIR /app/log
COPY backend /app/backend
COPY frontend /app/frontend
COPY entrypoint.sh /app/entrypoint.sh

WORKDIR /app/frontend
RUN rm -rf node_modules
RUN npm install
RUN quasar build
RUN chmod +x /app/entrypoint.sh

WORKDIR /app
