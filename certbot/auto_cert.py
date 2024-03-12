import os
from pathlib import Path
import time
import yaml

CLOUD_FLARE_INI_PATH = Path("/config/cloudflare.ini")
DOMAINS_YAML_PATH = Path('/config/domains.yml')


def get_certificates():
    if not CLOUD_FLARE_INI_PATH.exists():
        return
    if not DOMAINS_YAML_PATH.exists():
        return

    email: str = ''
    for line in CLOUD_FLARE_INI_PATH.read_text().splitlines():
        if line.startswith("dns_cloudflare_email"):
            email = line.split("=")[1].strip()
            break
    if not email:
        raise Exception("email not found")

    with DOMAINS_YAML_PATH.open() as domains_file:
        domains: list[str] = yaml.full_load(domains_file)
        if not domains:
            return
        for domain in domains:
            cmd = ("certbot certonly "
                   "--dns-cloudflare "
                   "--dns-cloudflare-propagation-seconds 60 "
                   f"--dns-cloudflare-credentials {CLOUD_FLARE_INI_PATH} "
                   "--agree-tos "
                   "--no-eff-email "
                   f"--email {email} "
                   "--non-interactive "
                   f'-d "{domain}"')
            os.system(cmd)


if __name__ == "__main__":
    while True:
        try:
            get_certificates()
        except BaseException as ex:
            print(ex)
        time.sleep(60)
