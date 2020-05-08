#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


from flask import Flask
from flask_login import LoginManager

from handlers import index, register, login, create_channel, grant, helpdesk, settings, delete, user_settings, \
    error_handlers
from storage.db_session import base_init

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

app.config["SECRET_KEY"] = "lithium_secret_key"

SessObject = base_init()

app.register_blueprint(index.create_handler(SessObject))
app.register_blueprint(register.create_handler(SessObject))
app.register_blueprint(login.create_handler(SessObject, login_manager))
app.register_blueprint(create_channel.create_handler(SessObject))
app.register_blueprint(grant.create_handler(SessObject))
app.register_blueprint(settings.create_handler(SessObject))
app.register_blueprint(helpdesk.create_handler())
app.register_blueprint(delete.create_handler(SessObject))
app.register_blueprint(user_settings.create_handler(SessObject))
app.register_error_handler(401, error_handlers.error_401)

if __name__ == "__main__":
    app.run(port=8077, host="0.0.0.0")
