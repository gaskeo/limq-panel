#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\
import os

from flask import Blueprint, send_from_directory
from . import RequestMethods


def get_root_path(app: Blueprint):
    return app.root_path.replace('handlers', '').strip('/').strip('\\')


def create_handler() -> Blueprint:
    """
    A closure for instantiating the handler
    that maintains favicon, manifest and other.
    Must borrow a SqlAlchemy session creator for further usage.
    """

    app = Blueprint("service", __name__)

    @app.route("/manifest.json", methods=[RequestMethods.GET])
    def manifest():
        """ Handler for main page """
        return send_from_directory(
            get_root_path(app),
            'manifest.json')

    @app.route("/asset-manifest.json", methods=[RequestMethods.GET])
    def asset_manifest():
        """ Handler for main page """
        return send_from_directory(
            get_root_path(app),
            'asset-manifest.json')

    @app.route("/robots.txt", methods=[RequestMethods.GET])
    def robots():
        """ Handler for main page """
        return send_from_directory(
            get_root_path(app),
            'robots.txt')

    @app.route("/browserconfig.xml", methods=[RequestMethods.GET])
    def browserconfig():
        """ Handler for main page """
        return send_from_directory(
            get_root_path(app),
            'browserconfig.xml')

    @app.route("/favicon/<favicon>", methods=[RequestMethods.GET])
    def favicons(favicon: str):
        return send_from_directory(
            os.path.join(get_root_path(app), 'favicon'), favicon)

    @app.route("/favicon.ico", methods=[RequestMethods.GET])
    def favicon_ico():
        return send_from_directory(get_root_path(app), 'favicon.ico')

    @app.route("/apple-touch-icon.png", methods=[RequestMethods.GET])
    def apple_touch_icon():
        """ Handler for main page """
        return send_from_directory(
            get_root_path(app),
            'apple-touch-icon.png')

    return app
