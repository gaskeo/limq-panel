from typing import ClassVar

from flask import Blueprint, render_template, redirect, request
from flask_login import current_user, login_required

from forms import ChangeEmail, ChangePassword, ChangeUsername
from storage.user import User
from errors import explain as explain_error


def create_handler(sess_cr: ClassVar) -> Blueprint:
    app = Blueprint("user_settings", __name__)

    @app.route("/edit_profile/<user_id>", methods=("GET", "POST"))
    @login_required
    def settings(user_id):
        error = request.args.get("error", None)
        sess = sess_cr()
        user: User = sess.query(User).filter(User.id == user_id).first()
        if not user:
            return redirect("/?error=user_invalid")
        if str(user_id) != str(current_user.id):
            return redirect("/?error=no_access_to_this_user")

        form_change_username = ChangeUsername()
        form_change_username.id.data = user_id
        form_change_username.new_username.data = user.username

        form_change_email = ChangeEmail()
        form_change_email.id.data = user_id
        form_change_email.new_email.data = user.email

        form_change_password = ChangePassword()
        form_change_password.id.data = user_id

        param = {"name_site": "Lithium MQ",
                 "form_change_username": form_change_username,
                 "form_change_email": form_change_email,
                 "form_change_password": form_change_password,
                 "error": explain_error(error) if error else None}

        return render_template("edit_profile.html", **param)

    @app.route("/do/change_username", methods=("POST",))
    @login_required
    def do_change_username():
        form = ChangeUsername()
        if not form.validate():
            return redirect("/?error=bad_request")

        user_id = form.id.data
        sess = sess_cr()

        user = sess.query(User).filter(User.id == int(user_id)).first()
        if not user:
            return redirect("/?error=user_invalid")

        if user.id != current_user.id:
            return redirect("/?error=no_access_to_this_user")

        user.username = form.new_username.data
        sess.commit()
        return redirect(f"/edit_profile/{user_id}")

    @app.route("/do/change_email", methods=("POST",))
    @login_required
    def do_change_email():
        form = ChangeEmail()
        email: str = form.new_email.data
        password: str = form.password.data
        user_id: str = form.id.data

        sess = sess_cr()

        user = sess.query(User).filter(User.id == user_id).first()
        if not user:
            return redirect("/?error=user_invalid")
        if not user.check_password(password):
            return redirect(f"/edit_profile/{user_id}?error=wrong_password#list-email-change")
        if user.id != current_user.id:
            return redirect("/?error=no_access_to_this_user")
        if sess.query(User).filter(User.email == email).first():
            return redirect(f"/edit_profile/{user_id}?error=email_exist#list-email-change")
        user.email = email
        sess.commit()

        return redirect(f"/edit_profile/{user_id}#list-email-change")

    @app.route("/do/change_password", methods=("POST",))
    @login_required
    def do_change_password():
        form = ChangePassword()
        old_password = form.old_password.data
        password = form.password.data
        password_again = form.password_again.data
        user_id = form.id.data

        sess = sess_cr()

        user: User = sess.query(User).filter(User.id == int(user_id)).first()

        if not user:
            return redirect("/?error=user_invalid")
        if not user.check_password(old_password):
            return redirect(f"/edit_profile/{user_id}?error=wrong_password#list-password-change")
        if user.id != current_user.id:
            return redirect("/?error=no_access_to_this_channel")
        if password_again != password:
            return redirect(f"/edit_profile/{user_id}?error=passwords_not_match#list-password-change")
        print(user.hashed_password)
        user.set_password(password)
        print(user.hashed_password)
        sess.commit()
        return redirect(f"/edit_profile/{user_id}#list-password-change")

    return app
