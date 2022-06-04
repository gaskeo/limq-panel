#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


from typing import ClassVar

from flask import Blueprint, abort, make_response

from forms import RegisterForm
from storage.user import User


def create_handler(sess_cr: ClassVar) -> Blueprint:
    """
    A closure for instantiating the handler that maintains register process.
    Must borrow a SqlAlchemy session creator for further usage.
    :param sess_cr: sqlalchemy.orm.sessionmaker object
    :return Blueprint object
    """

    app = Blueprint("register", __name__)

    @app.route("/do/register", methods=["POST"])
    def register():
        """ Handler for register """
        form = RegisterForm()

        if form.password.data != form.password_again.data:
            return abort(make_response(
                {'message': 'Passwords do not match'}, 401))

        session = sess_cr()

        if session.query(User).filter(User.email == form.email.data).first():
            return abort(make_response(
                {'message': 'User with this email already exists'}, 409))

        # noinspection PyArgumentList
        user = User(
            email=form.email.data,
            username=form.username.data
        )

        user.set_password(form.password.data)
        session.add(user)
        session.commit()

        return {"status": True, "path": "/login"}

    return app
