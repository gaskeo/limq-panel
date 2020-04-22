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
from storage.key import Key
from storage.db_session import base_init
from storage.keygen import chan_identifier, generate_key

from forms import RegisterForm, RegisterChannelForm, LoginForm, CreateKeyForm


app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

app.config["SECRET_KEY"] = "lithium_secret_key"

SessObject = base_init()


@login_manager.user_loader
def load_user(user_id):
    session = SessObject()
    return session.query(User).get(user_id)


@app.route("/")
def index():
    error = request.args['error'] if 'error' in request.args else None
    param = {"title": "LithiumMQ", "name_site": "Lithium MQ", "current_user": current_user}

    if current_user.is_authenticated:
        sess = SessObject()

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

    return render_template("base.html", **param)


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

    session = SessObject()

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


@app.route("/create_channel", methods=["GET", "POST"])
def create_channel():
    form = RegisterChannelForm()
    param = {"name_site": "Lithium MQ", "title": "Регистрация канала", "form": form}
    return render_template("create_channel.html", **param)


@app.route("/do/create_channel", methods=("POST", ))
def do_create_channel():
    form = RegisterChannelForm()

    if not current_user.is_authenticated:
        return redirect("/")

    session = SessObject()
    channel = Channel(
        name=form.name.data,
        is_active=True,
        id=chan_identifier(),
        owner_id=current_user.id
    )
    session.add(channel)
    session.commit()
    return redirect("/")


@app.route("/grant")
@login_required
def grant():
    f = CreateKeyForm()
    return render_template("create_key.html", form=f)


@app.route("/do/grant", methods=("GET", ))
@login_required
def do_grant():
    form = CreateKeyForm(request.args, csrf_enabled=False)

    if not form.validate():
        return redirect("/?error=bad_request")

    sess = SessObject()

    channel = form.channel.data

    print(channel)

    chan: Channel = sess.query(Channel).filter(Channel.id == channel).first()
    if not chan:
        return redirect("/?error=channel_invalid")

    if chan.owner_id != current_user.id:
        return redirect("/?error=no_access_to_this_channel")

    key_s = generate_key()
    key = Key(key=key_s, chan_id=channel)

    read = form.read.data
    write = form.write.data

    key.perm = write << 1 | read
    sess.add(key)

    sess.commit()

    return redirect("/?key=" + key_s)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0")

