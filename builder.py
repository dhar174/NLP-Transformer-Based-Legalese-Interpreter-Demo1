from requests.adapters import HTTPAdapter, Retry
import requests
from threading import Lock
from flask import Flask


class SubdomainDispatcher(object):

    def __init__(self, user, create_app):
        self.create_app = create_app
        self.lock = Lock()
        self.instances = {}

    def get_application(self, user):

        with self.lock:
            app = self.instances.get(user)
            if app is None:
                app = create_app(user)
                self.instances[user] = app
            return app

    def __call__(self, environ, start_response):
        app = self.get_application(self.user)
        return app(environ, start_response)


def create_app(user):
    app = Flask(__name__)

    with app.app_context():
        app.config['dispatcher'] = SubdomainDispatcher(user, create_app)
        app.config['USER'] = user
        app.config['TESTING'] = True
        app.config['DEBUG'] = True
        app.secret_key = "secret key"
        app.config['UPLOADED'] = False
        #app.config['filenamestr'] = ''
        return app
