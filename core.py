#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\

import os

from flask import Flask
from flask_login import LoginManager


from handlers import index, grant, \
    helpdesk, \
    error_handlers, user, channel, mixin, service

import limits

from storage.db_session import base_init
from redis_storage.redis_session import base_init as redis_base_init
from version import version

# Flask init
app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

app.config["SECRET_KEY"] = os.getenv('secret_key')


@app.after_request
def add_header(response):
    response.headers['X-Powered-By'] = version
    return response


# Database init
SessObject = base_init()
RedisSessObject = redis_base_init()

limit_generator = limits.limit_generator(app)

# Blueprints registration
app.register_blueprint(index.create_handler(limit_generator))
app.register_blueprint(
    channel.create_handler(
        SessObject, RedisSessObject, limit_generator)
)

app.register_blueprint(user.create_handler(SessObject, login_manager,
                                           limit_generator))
app.register_blueprint(mixin.create_handler(
    SessObject, RedisSessObject, limit_generator))
app.register_blueprint(grant.create_handler(
    SessObject, RedisSessObject, limit_generator))
app.register_blueprint(helpdesk.create_handler())
app.register_error_handler(401, error_handlers.error_401)
app.register_blueprint(service.create_handler())

if __name__ == "__main__":
    app.run(port=5000, host="127.0.0.1")
