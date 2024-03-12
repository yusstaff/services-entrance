from pathlib import Path
import re
from flask_jwt_extended import jwt_required
import yaml

from flask import Blueprint, Response, jsonify, request

from certbot.request.api import API
from certbot.data.domain import Domain
from certbot.request.add_domains import AddDomainsRequest, AddDomainsResponse
from certbot.request.get_account import GetAccountResponse
from certbot.request.get_domains import GetDomainsResponse
from certbot.request.modify_account import ModifyAccountRequest, ModifyAccountResponse
from certbot.request.remove_domains import RemoveDomainsRequest, RemoveDomainsResponse


certbot = Blueprint('certbot', __name__)

CERTIFICATES_PATH = Path('/etc/letsencrypt/live')
DOMAINS_YAML_PATH = Path('/config/domains.yml')
CLOUDFLARE_CONFIG_PATH = Path('/config/cloudflare.ini')

DOMAIN_PATTERN = re.compile(r'^(\*\.)?(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$')
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$')


def read_domains() -> list[Domain]:
    domains: list[Domain] = []
    if DOMAINS_YAML_PATH.exists():
        with DOMAINS_YAML_PATH.open() as file:
            domain_list: list[str] = yaml.full_load(file)
            if domain_list:
                domains: list[Domain] = [Domain(domain) for domain in domain_list]
    return domains


def write_domains(domains: list[Domain]) -> None:
    with DOMAINS_YAML_PATH.open('w') as file:
        yaml.dump([domain.domain for domain in domains], file)


def fetch_certificates_status(domains: list[Domain]) -> None:
    for domain in domains:
        certs_path = CERTIFICATES_PATH.joinpath(domain.domain.replace('*.', ''))
        certs_path = certs_path.joinpath('fullchain.pem')
        domain.hasCertificate = certs_path.exists()


def get_domains() -> Response:
    res = GetDomainsResponse()
    res.domains = read_domains()
    fetch_certificates_status(res.domains)

    return res


def add_domains() -> Response:
    req = AddDomainsRequest.get()

    for domain in req.domains:
        if not DOMAIN_PATTERN.match(domain):
            res = AddDomainsResponse()
            res.status = 5
            res.message = f'Invalid domain: {domain}.'
            return res

    new_domains: list[Domain] = []
    for domain in req.domains:
        new_domains.append(Domain(domain))
    fetch_certificates_status(new_domains)

    domains = read_domains() + new_domains
    write_domains(domains)

    res = AddDomainsResponse()
    res.domains = new_domains

    return res


def remove_domains() -> Response:
    req = RemoveDomainsRequest.get()
    deleted = [Domain(**d) for d in req.domains]

    domains = read_domains()
    domains = [domain for domain in domains if not any(domain.domain == rd.domain for rd in deleted)]
    write_domains(domains)

    res = RemoveDomainsResponse()
    res.domains = req.domains

    return res


@certbot.route(API.DOMAINS, methods=['GET', 'POST', 'DELETE'])
@jwt_required()
def domains() -> Response:
    if request.method == 'GET':
        return jsonify(get_domains())
    elif request.method == 'POST':
        return jsonify(add_domains())
    elif request.method == 'DELETE':
        return jsonify(remove_domains())


def get_account() -> Response:
    if CLOUDFLARE_CONFIG_PATH.exists():
        for line in CLOUDFLARE_CONFIG_PATH.read_text().splitlines():
            if line.startswith('dns_cloudflare_email'):
                email = line.split("=")[1].strip()

    res = GetAccountResponse()
    res.email = email

    return res


def modify_account() -> Response:
    req = ModifyAccountRequest.get()

    if not EMAIL_PATTERN.match(req.email):
        res = ModifyAccountResponse()
        res.status = 5
        res.message = 'Invalid email.'
        return res
    if not req.api_key:
        res = ModifyAccountResponse()
        res.status = 3
        res.message = 'Empty api key.'
        return res

    CLOUDFLARE_CONFIG_PATH.write_text(
        f'dns_cloudflare_email={req.email}\n'
        f'dns_cloudflare_api_key={req.api_key}\n'
    )

    res = ModifyAccountResponse()
    res.email = req.email

    return res


@certbot.route(API.ACCOUNT, methods=['GET', 'POST'])
@jwt_required()
def account() -> Response:
    if request.method == 'GET':
        return jsonify(get_account())
    elif request.method == 'POST':
        return jsonify(modify_account())
