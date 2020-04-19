#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


from flask import Flask, render_template, redirect, request, make_response, abort
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

from data import db_session
from data.users import User

from data.db_session import create_session, global_init

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

app.config["SECRET_KEY"] = "lithium_secret_key"
global_init("db/Users.sqlite")


class LoginForm(FlaskForm):
    email = StringField("Электропочта", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember_me = BooleanField("Запомнить меня")

    submit = SubmitField("Войти")


class RegisterForm(FlaskForm):
    email = StringField("Электропочта", validators=[DataRequired()])
    username = StringField("Ваше имя", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    password_again = PasswordField("Еще раз пароль", validators=[DataRequired()])
    submit = SubmitField("Зарегистрироваться")


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route("/")
def index():
    param = dict()
    param["title"] = "title"
    param["name_site"] = "Lithium MQ"
    param["current_user"] = current_user
    return render_template("base.html", **param)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    param = dict()
    param["name_site"] = "Lithium MQ"
    param["title"] = "Регистрация"
    param["form"] = form
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template("reg_form.html", title="Регистрация",
                                   form=form,
                                   message="Пароли не совпадают")
        session = create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            param["message"] = "Пользователь с таким email уже существует"
            return render_template("reg_form.html", **param)
        user = User(
            email=form.email.data,
            username=form.username.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect("/login")

    return render_template("reg_form.html", **param)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    param = dict()
    param["name_site"] = "Lithium MQ"
    param["form"] = form
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/")
        return render_template("login.html",
                               message="Неправильный логин или пароль",
                               form=form)

    return render_template("login.html", title="Авторизация", **param)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == "__main__":
    app.run(port=8080, host="127.0.0.1")
