#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


from typing import ClassVar

from flask import Blueprint, render_template, redirect
from flask_login import LoginManager, login_user

from forms import LoginForm
from storage.user import User


def create_handler(sess_cr: ClassVar, lm: LoginManager) -> Blueprint:
    """
    A closure for instantiating the handler that maintains login process.
    Must borrow a SqlAlchemy session creator for further usage.
    :param sess_cr: sqlalchemy.orm.sessionmaker class
    :return Blueprint class
    """

    app = Blueprint("login", __name__)

    @lm.user_loader
    def load_user(user_id):
        """ Function for loading the user """

        session = sess_cr()
        return session.query(User).get(user_id)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """ Handler for login """
        form = LoginForm()

        param = {"name_site": "Lithium MQ", "form": form}

        if form.validate_on_submit():
            # User validation
            sess = sess_cr()
            user = sess.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                return redirect("/")
            return render_template("login.html",
                                   message="Неправильный логин или пароль",
                                   form=form)

        return render_template("login.html", title="Авторизация", **param)

    return app
