from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
import secrets
import yaml

from flask import Blueprint, Response, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_csrf_token,
    get_jwt,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
    get_jwt_identity,
    jwt_required,
    JWTManager
)
from werkzeug.security import generate_password_hash, check_password_hash

from app_instance import AppInstance
from auth.request.api import API
from auth.request.login import LoginRequest, LoginResponse
from auth.request.logout import LogoutResponse
from auth.request.refresh import RefreshResponse
from auth.request.unregister import UnregisterResponse
from auth.request.verify import VerifyResponse

auth = Blueprint('auth', __name__)

AUTH_PATH = Path('/config/auth')
if not AUTH_PATH.exists():
    with AUTH_PATH.open('w') as file:
        yaml.safe_dump({
            'secret': secrets.token_hex(32),
            'username': None,
            'password': None,
        }, file)

with AUTH_PATH.open() as file:
    auth_data = yaml.safe_load(file)
    SECRET: str = auth_data['secret']
    USERNAME: str = auth_data['username']
    PASSWORD: str = auth_data['password']

app = AppInstance.get()
app.config["JWT_SECRET_KEY"] = SECRET
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_CSRF_IN_COOKIES'] = True
jwt = JWTManager(app)

USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]{5,20}$')
PASSWORD_PATTERN = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,32}$')


@auth.route(API.LOGIN, methods=["POST"])
def login() -> Response:
    global USERNAME
    global PASSWORD
    req = LoginRequest.get()

    if not req.username or not USERNAME_PATTERN.match(req.username):
        res = LoginResponse()
        res.status = 5
        res.message = 'Username: 5-20 chars, A-Z, a-z, 0-9, _.'
        return jsonify(res)
    if not req.password or not PASSWORD_PATTERN.match(req.password):
        res = LoginResponse()
        res.status = 5
        res.message = 'Password: 8-32 chars, includes A-Z, a-z, 0-9, !@#$%^&*.'
        return jsonify(res)

    if not USERNAME or not PASSWORD:
        USERNAME = req.username
        PASSWORD = generate_password_hash(req.password)
        with AUTH_PATH.open('w') as file:
            yaml.safe_dump({
                'secret': SECRET,
                'username': USERNAME,
                'password': PASSWORD,
            }, file)
    elif req.username != USERNAME or not check_password_hash(PASSWORD, req.password):
        res = LoginResponse()
        res.status = 3
        res.message = 'Bad username or password'
        return jsonify(res)

    access_token = create_access_token(identity=USERNAME, fresh=True)
    refresh_token = create_refresh_token(identity=USERNAME)
    csrf_access_token = get_csrf_token(access_token)
    csrf_refresh_token = get_csrf_token(refresh_token)

    res = LoginResponse()
    res.csrf_access_token = csrf_access_token
    res.csrf_refresh_token = csrf_refresh_token
    res = jsonify(res)
    set_access_cookies(res, access_token)
    set_refresh_cookies(res, refresh_token)
    return res


@auth.route(API.LOGOUT, methods=["POST"])
def logout():
    res = jsonify(LogoutResponse())
    unset_jwt_cookies(res)
    return res


@auth.route(API.REFRESH, methods=["POST"])
@jwt_required(refresh=True)
def refresh() -> Response:
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity, fresh=False)
    csrf_access_token = get_csrf_token(access_token)

    res = RefreshResponse()
    res.csrf_access_token = csrf_access_token
    res = jsonify(res)
    set_access_cookies(res, access_token)
    return res


@auth.route(API.VERIFY, methods=["GET"])
@jwt_required(optional=True)
def verify():
    identity = get_jwt_identity()
    res = VerifyResponse()
    res.verified = identity is not None
    res = jsonify(res)
    return res


@auth.route(API.UNREGISTER, methods=["DELETE"])
@jwt_required()
def unregister():
    global USERNAME
    global PASSWORD
    USERNAME = None
    PASSWORD = None

    with AUTH_PATH.open('w') as file:
        yaml.safe_dump({
            'secret': SECRET,
            'username': '',
            'password': '',
        }, file)

    res = jsonify(UnregisterResponse())
    unset_jwt_cookies(res)
    return res


@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response
