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

from storage.user import User
from storage.channel import Channel
from storage.db_session import base_init
from storage.keygen import chan_identifier

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

app.config["SECRET_KEY"] = "lithium_secret_key"

SessObject = base_init()


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


class RegisterChannel(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    submit = SubmitField('Создать канал')


@login_manager.user_loader
def load_user(user_id):
    session = SessObject()
    return session.query(User).get(user_id)


@app.route("/")
def index():
    error = request.args['error'] if 'error' in request.args else None
    param = {"title": "LithiumMQ", "name_site": "Lithium MQ",
             "current_user": current_user, "error": error}

    if current_user.is_authenticated:
        sess = SessObject()
        channels = sess.query(Channel).filter(Channel.owner_id == current_user.id).all()
        if channels:
            param["user_channels"] = channels

    return render_template("base.html", **param)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    param = {"name_site": "Lithium MQ", "title": "Регистрация", "form": form}

    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template("reg_form.html", title="Регистрация",
                                   form=form,
                                   message="Пароли не совпадают")
        sess = SessObject()
        if sess.query(User).filter(User.email == form.email.data).first():
            param["message"] = "Пользователь с таким email уже существует"
            return render_template("reg_form.html", **param)

        # noinspection PyArgumentList
        user = User(
            email=form.email.data,
            username=form.username.data
        )

        user.set_password(form.password.data)
        sess.add(user)
        sess.commit()

        return redirect("/login")

    return render_template("reg_form.html", **param)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    param = {"name_site": "Lithium MQ", "form": form}

    if form.validate_on_submit():
        sess = SessObject()
        user = sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/")
        return render_template("login.html",
                               message="Неправильный логин или пароль",
                               form=form)

    return render_template("login.html", title="Авторизация", **param)


@app.route('/create_channel', methods=['GET', 'POST'])
def create_channel():
    form = RegisterChannel()
    param = {'name_site': 'Lithium MQ', 'title': 'Регистрация канала', 'form': form}
    return render_template('create_channel.html', **param)


@app.route('/do_create_channel', methods=('POST', ))
def do_create_channel():
    form = RegisterChannel()

    if current_user.is_authenticated:
        sess = SessObject()
        channel = Channel(
            name=form.name.data,
            is_active=True,
            id=chan_identifier(),
            owner_id=current_user.id
        )
        sess.add(channel)
        sess.commit()
    error = 'bad request'
    return redirect(f'/?{"error=" + error if error else ""}')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0")

