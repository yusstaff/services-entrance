from flask import Flask


class AppInstance(object):

    instance: Flask = None

    @staticmethod
    def get() -> Flask:
        return AppInstance.instance

    @staticmethod
    def set(app: Flask) -> None:
        AppInstance.instance = app
