import os
from pathlib import Path
import re

from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import jwt_required
import yaml
from openvpn.data.subnet import Subnet

from openvpn.request.api import API
from openvpn.request.get_subnets import GetSubnetsResponse
from openvpn.request.modify_subnets import ModifySubnetsRequest, ModifySubnetsResponse


openvpn = Blueprint('openvpn', __name__)

SUBNET_CONFIG_PATH: Path = Path('/config/subnets.yaml')
OPENVPN_CONTAIN_NAME: str = 'ykw-openvpn-as'

SUBNET_ADDRESS_PATTERN = re.compile(
    r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
    r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
    r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
    r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')


def get_subnets() -> GetSubnetsResponse:
    subnets: list[Subnet] = []
    if SUBNET_CONFIG_PATH.exists():
        with SUBNET_CONFIG_PATH.open() as file:
            config_data: list[dict] = yaml.safe_load(file)
            if config_data:
                for subnet in config_data:
                    subnets.append(Subnet(subnet['address'], int(subnet['cidr'])))

    res = GetSubnetsResponse()
    res.subnets = subnets

    return res


def __set_subnets(subnets: list[Subnet]) -> None:
    for subnet in subnets:
        cmd = (f'next_hop_ip=$(dig +short {OPENVPN_CONTAIN_NAME}) && '
               f'ip route replace {subnet.address}/{subnet.cidr} via $next_hop_ip dev eth0')
        os.system(cmd)


def __unset_subnets(subnets: list[Subnet]) -> None:
    for subnet in subnets:
        cmd = (f'next_hop_ip=$(dig +short {OPENVPN_CONTAIN_NAME}) && '
               f'ip route del {subnet.address}/{subnet.cidr}')
        os.system(cmd)


def modify_subnets() -> ModifySubnetsResponse:
    req = ModifySubnetsRequest.get()

    for subnet in req.subnets:
        if not SUBNET_ADDRESS_PATTERN.match(subnet.address):
            res = ModifySubnetsResponse()
            res.status = 5
            res.message = f'Wrong subnet address {subnet.address}/{subnet.cidr}.'
            return res
        elif subnet.cidr < 16 or subnet.cidr > 32:
            res = ModifySubnetsResponse()
            res.status = 5
            res.message = f'Wrong subnet CIDR {subnet.address}/{subnet.cidr}. CIDR: 16-32.'
            return res

    old_subnets = get_subnets().subnets

    with SUBNET_CONFIG_PATH.open('w') as file:
        subnets = [subnet.__dict__ for subnet in req.subnets]
        yaml.safe_dump(subnets, file)

    __unset_subnets(old_subnets)
    __set_subnets(req.subnets)

    res = ModifySubnetsResponse()
    res.subnets = req.subnets

    return res


@openvpn.route(API.subnet, methods=['GET', 'POST'])
@jwt_required()
def subnets() -> Response:
    if request.method == 'GET':
        return jsonify(get_subnets())
    elif request.method == 'POST':
        return jsonify(modify_subnets())


__set_subnets(get_subnets().subnets)
