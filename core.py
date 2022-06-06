#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


from flask import Flask
from flask_login import LoginManager

from handlers import index, grant, \
    helpdesk, \
    error_handlers, user, channel, mixin
from storage.db_session import base_init

# Flask init
app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

app.config["SECRET_KEY"] = "lithium_secret_key"

# Database init
SessObject = base_init()

# Blueprints registration
app.register_blueprint(index.create_handler(SessObject))
app.register_blueprint(channel.create_handler(SessObject))
app.register_blueprint(user.create_handler(SessObject, login_manager))
app.register_blueprint(mixin.create_handler(SessObject))
app.register_blueprint(grant.create_handler(SessObject))
app.register_blueprint(helpdesk.create_handler())
app.register_error_handler(401, error_handlers.error_401)

if __name__ == "__main__":
    app.run(port=8077, host="0.0.0.0")
