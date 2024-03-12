import importlib
import os

from flask import Blueprint, Flask
from flask_cors import CORS

from app_instance import AppInstance

app = Flask(__name__)
AppInstance.set(app)
CORS(app,
     origins='http://localhost:*',
     supports_credentials=True,
     allow_headers=[
         'Content-Type',
         'Authorization',
         'X-CSRF-TOKEN'])


def register_blueprints(root_pkg_path: str):
    project_root_path = os.path.dirname(__file__)
    os.chdir(project_root_path)
    for dirpath, _, filenames in os.walk(root_pkg_path):
        for filename in filenames:
            if filename.endswith('.py') and filename != '__init__.py':
                module_rel_path = os.path.relpath(dirpath, project_root_path).replace(os.sep, '.')
                module_name = f"{module_rel_path}.{filename[:-3]}"
                print(module_name)
                module = importlib.import_module(module_name)

                for item in dir(module):
                    item = getattr(module, item)
                    if isinstance(item, Blueprint):
                        app.register_blueprint(item)


register_blueprints('auth/blueprint')
register_blueprints('wireguard/blueprint')
register_blueprints('certbot/blueprint')
register_blueprints('envoy/blueprint')
register_blueprints('openvpn/blueprint')
