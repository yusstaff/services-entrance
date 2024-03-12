from flask import request
from werkzeug.exceptions import BadRequest


class BaseRequest(object):
    @classmethod
    def __from_args(cls):
        req = cls()
        jso: dict = {attr_name: request.args.get(attr_name, default=None) for attr_name in req.__dict__.keys()}
        req.parse(jso)
        return req

    @classmethod
    def __from_form(cls):
        req = cls()
        jso: dict = {attr_name: request.form.get(attr_name, default=None) for attr_name in req.__dict__.keys()}
        req.parse(jso)
        return req

    @classmethod
    def __from_json(cls):
        req = cls()
        jso: dict = request.get_json()
        jso = {attr_name: jso.get(attr_name, None) for attr_name in req.__dict__.keys()}
        req.parse(jso)
        return req

    @classmethod
    def get(cls):
        if request.method == 'GET':
            return cls.__from_args()
        elif request.method == 'POST' or request.method == 'DELETE':
            if request.content_type == 'application/json':
                return cls.__from_json()
            elif request.content_type == 'application/x-www-form-urlencoded':
                return cls.__from_form()

        raise BadRequest('Unsupported request.')

    def parse(self, jso: dict) -> None:
        for attr_name, value in jso.items():
            setattr(self, attr_name, value)
