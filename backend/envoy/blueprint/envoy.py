import os
from pathlib import Path

from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import jwt_required
import yaml
from envoy.data.config import Config

from envoy.request.api import API
from envoy.request.get_proxy import GetProxyResponse
from envoy.request.modify_proxy import ModifyProxyRequest, ModifyProxyResponse


envoy = Blueprint('envoy', __name__)

LOCAL_CONFIG_PATH: Path = Path('/config/envoy-local.yaml')
ENVOY_CONFIG_PATH: Path = Path('/config/envoy.yaml')
RESTART_EPOCH_PATH: Path = Path('/config/envoy-restart-epoch.txt')
LOG_PATH: Path = Path('/app/log/envoy.log')

restart_epoch: int = 1


def get_proxy() -> Response:
    if LOCAL_CONFIG_PATH.exists():
        with LOCAL_CONFIG_PATH.open() as file:
            config_data = yaml.safe_load(file)
        config = Config.parse(config_data)
    else:
        config = Config.createExample()

    res = GetProxyResponse()
    res.config = config

    return res


def modify_proxy() -> Response:
    req = ModifyProxyRequest.get()

    config = Config.parse(req.config)
    try:
        config.validate()
    except Exception as ex:
        res = ModifyProxyResponse()
        res.status = 5
        res.message = ex.args[0]
        return res

    with ENVOY_CONFIG_PATH.open('w') as file:
        yaml.safe_dump(config.toDict(), file)
    with LOCAL_CONFIG_PATH.open('w') as file:
        yaml.safe_dump(req.config, file)

    if RESTART_EPOCH_PATH.exists():
        epoch = int(RESTART_EPOCH_PATH.read_text().strip())
    else:
        epoch = 0

    RESTART_EPOCH_PATH.write_text(str(epoch + 1))

    restart_cmd = f'nohup envoy -c {ENVOY_CONFIG_PATH} --base-id 0 --restart-epoch {epoch} > {LOG_PATH} 2>&1  &'
    os.system(restart_cmd)

    res = ModifyProxyResponse()

    return res


@envoy.route(API.PROXY, methods=['GET', 'POST'])
@jwt_required()
def proxy() -> Response:
    if request.method == 'GET':
        return jsonify(get_proxy())
    elif request.method == 'POST':
        return jsonify(modify_proxy())
