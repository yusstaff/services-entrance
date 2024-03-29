from pathlib import Path

from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import jwt_required
from data.subnet import read_subnets, save_subnets, set_subnets, unset_subnets, validate_subnets

from openvpn.request.api import API
from openvpn.request.get_subnets import GetSubnetsResponse
from openvpn.request.modify_subnets import ModifySubnetsRequest, ModifySubnetsResponse

openvpn = Blueprint('openvpn', __name__)

SUBNET_CONFIG_PATH: Path = Path('/config/subnets-openvpn.yaml')
CONTAIN_NAME: str = 'ykw-openvpn-as'


def get_subnets() -> GetSubnetsResponse:
    res = GetSubnetsResponse()
    res.subnets = read_subnets(SUBNET_CONFIG_PATH)
    return res


def modify_subnets() -> ModifySubnetsResponse:
    req = ModifySubnetsRequest.get()

    if error_msg := validate_subnets(req.subnets):
        res = ModifySubnetsResponse()
        res.status = 5
        res.message = error_msg
        return res

    old_subnets = read_subnets(SUBNET_CONFIG_PATH)

    save_subnets(SUBNET_CONFIG_PATH, req.subnets)

    unset_subnets(old_subnets, CONTAIN_NAME)
    set_subnets(req.subnets, CONTAIN_NAME)

    res = ModifySubnetsResponse()
    res.subnets = req.subnets

    return res


@openvpn.route(API.SUBNETS, methods=['GET', 'POST'])
@jwt_required()
def subnets() -> Response:
    if request.method == 'GET':
        return jsonify(get_subnets())
    elif request.method == 'POST':
        return jsonify(modify_subnets())


set_subnets(read_subnets(SUBNET_CONFIG_PATH), CONTAIN_NAME)
