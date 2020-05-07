#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


from typing import ClassVar

from flask import Blueprint, render_template, request, redirect
from flask_login import current_user, login_required, logout_user

from errors import explain as explain_error
from storage.channel import Channel
from storage.key import Key
from forms import RegisterForm
from storage.user import User


def create_handler(sess_cr: ClassVar) -> Blueprint:
    """
    A closure for instantiating the handler that maintains mainpage.
    Must borrow a SqlAlchemy session creator for further usage.
    :param sess_cr: sqlalchemy.orm.sessionmaker class
    :return Blueprint class
    """

    app = Blueprint("index", __name__)

    @app.route("/", methods=["GET", "POST"])
    def index():
        """ Handler for main page """

        error = request.args.get("error", None)
        param = {"title": "LithiumMQ", "name_site": "Lithium MQ", "current_user": current_user,
                 "error": explain_error(error) if error else None}
        if current_user.is_authenticated:

            param = {"title": "LithiumMQ", "name_site": "Lithium MQ", "current_user": current_user,
                     "error": explain_error(error) if error else None}

            if current_user.is_authenticated:
                sess = sess_cr()

                channels = sess.query(Channel).filter(Channel.owner_id == current_user.id).all()

                if channels:
                    key_stats = [...] * len(channels)

                    for i, chan in enumerate(channels):
                        r, w = 0, 0
                        keys_assoc = sess.query(Key).filter(Key.chan_id == chan.id).all()
                        for key in keys_assoc:
                            if key.can_write():
                                w += 1
                            if key.can_read():
                                r += 1
                        key_stats[i] = r, w

                    param["user_channels"] = channels
                    param["user_channels_stat"] = key_stats

            return render_template("mainpage.html", **param)
        else:
            form = RegisterForm()

            param["form"] = form
            if not form.validate_on_submit():
                return render_template("mainpage.html", **param)

            if form.password.data != form.password_again.data:
                return render_template("mainpage.html",
                                       form=form,
                                       message="Пароли не совпадают")

            session = sess_cr()

            if session.query(User).filter(User.email == form.email.data).first():
                param["message"] = "Пользователь с таким email уже существует"
                return render_template("mainpage.html", **param)

            # noinspection PyArgumentList
            user = User(
                email=form.email.data,
                username=form.username.data
            )

            user.set_password(form.password.data)
            session.add(user)
            session.commit()
            return redirect("/login")

    @app.route("/logout")
    @login_required
    def logout():
        """ Handler for logout """
        logout_user()
        return redirect("/")

    return app
