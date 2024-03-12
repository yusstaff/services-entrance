from pathlib import Path
import re
import shutil
import subprocess

from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import jwt_required

from wireguard.request.api import API
from wireguard.data.peer import Peer
from wireguard.request.add_peers import AddPeersRequest, AddPeersResponse
from wireguard.request.download_peer import DownloadPeerRequest, DownloadPeerResponse
from wireguard.request.get_peers import GetPeersResponse
from wireguard.request.remove_peers import RemovePeersRequest, RemovePeersResponse


wireguard = Blueprint('wireguard', __name__)

PEERS_PATTERN = re.compile(r'[^,=]+')
PEERS_ENV_PATH = '/config/peers.env'
DEFAULT_PEER_NAME = 'WG_DEFAULT_PEER'

PEER_NAME_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9]{4,15}$')


def get_peer_path(name: str) -> Path:
    return Path(f'/config/peer_{name}')


def get_peer_conf_path(name: str) -> Path:
    return get_peer_path(name).joinpath(f'peer_{name}.conf')


def get_peer_png_path(name: str) -> Path:
    return get_peer_path(name).joinpath(f'peer_{name}.png')


def get_peer_privatekey_path(name: str) -> Path:
    return get_peer_path(name).joinpath(f'privatekey-peer_{name}')


def get_peer_publickey_path(name: str) -> Path:
    return get_peer_path(name).joinpath(f'publickey-peer_{name}')


def get_peer_presharedkey_path(name: str) -> Path:
    return get_peer_path(name).joinpath(f'presharedkey-peer_{name}')


def get_peers(peers: list[str]) -> GetPeersResponse:
    peer_list: list[Peer] = []
    for peer_name in peers:
        peer_path = get_peer_conf_path(peer_name)
        if not peer_path.exists():
            peer = Peer()
            peer.name = peer_name

            peer_list.append(peer)
        else:
            peer_conf = peer_path.read_text().splitlines()

            peer = Peer()
            peer.name = peer_name
            peer.address = peer_conf[1].split('=')[1]

            private_key = peer_conf[2].split(' ')[2]

            pipe = subprocess.PIPE
            process1 = subprocess.Popen(['echo', private_key], stdout=pipe, text=True)
            process2 = subprocess.Popen(['wg', 'pubkey'], stdin=process1.stdout, stdout=pipe, text=True)
            process1.stdout.close()
            output = process2.communicate()[0]
            peer.public_key = output

            peer_list.append(peer)

    res = GetPeersResponse()
    res.peers = peer_list

    return res


def add_peers(peers: list[str]) -> AddPeersResponse:
    req = AddPeersRequest.get()

    for peer in req.peers:
        if not PEER_NAME_PATTERN.match(peer):
            res = AddPeersResponse()
            res.status = 5
            res.message = "Name: 5-16 chars, A-Z, a-z, 0-9, The first character cannot be a digit."
            return res

    for new_peer_name in req.peers:
        if new_peer_name in peers:
            continue
        peers.append(new_peer_name)

    peers.insert(0, DEFAULT_PEER_NAME)
    Path(PEERS_ENV_PATH).write_text(f'PEERS={",".join(peers)}')

    res = AddPeersResponse()
    res.peers = [Peer(name) for name in req.peers]

    return res


def remove_peers(peers: list[str]) -> RemovePeersResponse:
    req = RemovePeersRequest.get()
    deleted = [Peer(**p) for p in req.peers]

    peers = [peer for peer in peers if not any(peer == rd.name for rd in deleted)]
    for peer_name in req.peers:
        peer_path = get_peer_path(peer_name)
        if peer_path.exists():
            shutil.rmtree(peer_path)

    peers.insert(0, DEFAULT_PEER_NAME)
    Path(PEERS_ENV_PATH).write_text(f'PEERS={",".join(peers)}')

    res = RemovePeersResponse()
    res.peers = req.peers

    return res


@wireguard.route(API.PEERS, methods=['GET', 'POST', 'DELETE'])
@jwt_required()
def peers() -> Response:
    peers_env = Path(PEERS_ENV_PATH).read_text()
    peers = PEERS_PATTERN.findall(peers_env)[2:]

    if request.method == 'GET':
        return jsonify(get_peers(peers))
    elif request.method == 'POST':
        return jsonify(add_peers(peers))
    elif request.method == 'DELETE':
        return jsonify(remove_peers(peers))


@wireguard.route(API.DOWNLOAD_PEER, methods=['POST'])
@jwt_required()
def download_peer() -> Response:
    req = DownloadPeerRequest.get()

    peer_path = get_peer_conf_path(req.peer)

    res = DownloadPeerResponse()
    if peer_path.exists():
        res.peer = peer_path.read_text()
    else:
        res.status = 3
        res.message = f'Cannot found peer {req.peer}.'

    return jsonify(res)
