#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


from typing import ClassVar

from flask import Blueprint, render_template, redirect

from forms import RegisterForm
from storage.user import User


def create_handler(sess_cr: ClassVar) -> Blueprint:
    app = Blueprint("register", __name__)

    @app.route("/register", methods=["GET", "POST"])
    def register():
        form = RegisterForm()

        param = {"name_site": "Lithium MQ", "title": "Регистрация", "form": form}

        if not form.validate_on_submit():
            return render_template("reg_form.html", **param)

        if form.password.data != form.password_again.data:
            return render_template("reg_form.html", title="Регистрация",
                                   form=form,
                                   message="Пароли не совпадают")

        session = sess_cr()

        if session.query(User).filter(User.email == form.email.data).first():
            param["message"] = "Пользователь с таким email уже существует"
            return render_template("reg_form.html", **param)

        # noinspection PyArgumentList
        user = User(
            email=form.email.data,
            username=form.username.data
        )

        user.set_password(form.password.data)
        session.add(user)
        session.commit()

        return redirect("/login")

    return app
