from typing import ClassVar

from flask import Blueprint, render_template, redirect, request
from flask_login import current_user, login_required

from errors import explain as explain_error
from forms import ChangeEmailForm, ChangePasswordForm, ChangeUsernameForm
from storage.user import User


def hide_email(e: str) -> str:
    """
    Hides an e-mail under the asterisks.

    :param e: e-mail
    :return hidden

    """

    if len(e) < 3:
        return ""

    name, full_domain = e.split("@")
    domain, zone = full_domain.split(".")

    name = name[0] + "*" * (len(name) - 2) + name[-1]
    domain = domain[0] + "*" * (len(domain) - 2) + domain[-1]

    return f"{name}@{domain}.{zone}"


def create_handler(sess_cr: ClassVar) -> Blueprint:
    """
    A closure for instantiating the handler that maintains user settings process.
    Must borrow a SqlAlchemy session creator for further usage.
    :param sess_cr: sqlalchemy.orm.sessionmaker object
    :return Blueprint object
    """

    app = Blueprint("user_settings", __name__)

    @app.route("/edit_profile", methods=("GET", "POST"))
    @login_required
    def settings():
        """ Handler for user settings """
        error = request.args.get("error", None)
        sess = sess_cr()

        # User validation
        user: User = sess.query(User).filter(User.id == current_user.id).first()
        if not user:
            return redirect("/?error=user_invalid")

        form_change_username = ChangeUsernameForm()
        form_change_username.new_username.data = user.username

        form_change_email = ChangeEmailForm()
        form_change_email.new_email.render_kw = {
            "placeholder": hide_email(user.email)
        }

        form_change_password = ChangePasswordForm()

        param = {"name_site": "Lithium MQ",
                 "form_change_username": form_change_username,
                 "form_change_email": form_change_email,
                 "form_change_password": form_change_password,
                 "error": explain_error(error) if error else None}

        return render_template("edit_profile.html", **param)

    @app.route("/do/change_username", methods=("POST",))
    @login_required
    def do_change_username():
        form = ChangeUsernameForm()
        if not form.validate():
            return redirect("/?error=bad_request")

        sess = sess_cr()

        user = sess.query(User).filter(User.id == current_user.id).first()
        if not user:
            return redirect("/?error=user_invalid")

        user.username = form.new_username.data
        sess.commit()
        return redirect("/edit_profile")

    @app.route("/do/change_email", methods=("POST",))
    @login_required
    def do_change_email():
        """ E-mail changing handler. """

        form = ChangeEmailForm()
        email: str = form.new_email.data
        password: str = form.password.data

        sess = sess_cr()

        # User validation

        user: User = sess.query(User).filter(User.id == current_user.id).first()

        if not user:
            return redirect("/?error=user_invalid")
        if not user.check_password(password):
            return redirect("/edit_profile?error=wrong_password#list-email-change")

        if sess.query(User).filter(User.email == email).first():
            return redirect("/edit_profile?error=email_already_exists#list-email-change")

        user.email = email
        sess.commit()

        return redirect("/edit_profile#list-email-change")

    @app.route("/do/change_password", methods=("POST",))
    @login_required
    def do_change_password():
        """ Password changing handler. """

        form = ChangePasswordForm()
        old_password: str = form.old_password.data
        password: str = form.password.data

        sess = sess_cr()

        # User validation

        user: User = sess.query(User).filter(User.id == current_user.id).first()

        if not user:
            return redirect("/?error=user_invalid")
        if not user.check_password(old_password):
            return redirect("/edit_profile?error=wrong_password#list-password-change")

        user.set_password(password)

        sess.commit()
        return redirect("/edit_profile#list-password-change")

    return app
