#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


from datetime import datetime
from typing import Iterable

from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from sqlalchemy import desc

from errors import explain as explain_error
from forms import RegisterForm, RegisterChannelForm, LoginForm, CreateKeyForm, \
    MainSettingsChannelForm, CreateMixin
from storage.channel import Channel
from storage.db_session import base_init
from storage.key import Key
from storage.keygen import chan_identifier, generate_key
from storage.user import User

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
    error = request.args.get("error", None)

    param = {"title": "LithiumMQ", "name_site": "Lithium MQ", "current_user": current_user,
             "error": explain_error(error) if error else None}

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

    return render_template("mainpage.html", **param)


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


@app.route("/do/create_channel", methods=("POST",))
@login_required
def do_create_channel():
    form = RegisterChannelForm()

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
    uid = current_user.id
    sess = SessObject()

    channels = sess.query(Channel).filter(Channel.owner_id == uid).all()

    return render_template("create_key.html", form=f, channels=channels)


@app.route("/do/grant", methods=("POST",))
@login_required
def do_grant():
    form = CreateKeyForm(request.form)

    if not form.validate():
        print(form.errors)
        return redirect("/?error=bad_request")

    sess = SessObject()

    channel = form.id.data

    chan: Channel = sess.query(Channel).filter(Channel.id == channel).first()
    if not chan:
        return redirect("/?error=channel_invalid")

    if chan.owner_id != current_user.id:
        return redirect("/?error=no_access_to_this_channel")

    key_s = generate_key()
    key = Key(key=key_s, chan_id=channel, name=form.name.data, created=datetime.now())

    read = form.read.data
    write = form.write.data
    info = form.info_allowed.data

    key.perm = info << 2 | write << 1 | read
    sess.add(key)

    sess.commit()

    return redirect(f"/settings/{channel}#list-keys-open")


# tmp
def perm_formatter(k: Key) -> str:
    r, w = k.can_read(), k.can_write()
    if r and w:
        return f"Приём, отправка / создан {k.created.date()}"
    if r:
        return f"Приём / создан {k.created.date()}"
    if w:
        return f"Отправка / создан {k.created.date()}"
    return f"Прав доступа не установлено / создан {k.created.date()}"


@app.route("/settings/<channel_id>", methods=("GET", "POST"))
@login_required
def settings(channel_id):
    sess = SessObject()
    chan: Channel = sess.query(Channel).filter(Channel.id == channel_id).first()
    if not chan:
        return redirect("/?error=channel_invalid")

    if chan.owner_id != current_user.id:
        return redirect("/?error=no_access_to_this_channel")

    form_main_settings = MainSettingsChannelForm()
    form_main_settings.id.data = channel_id
    form_main_settings.name.data = chan.name
    form_main_settings.is_active.data = chan.is_active

    form_keys = CreateKeyForm()
    form_keys.id.data = channel_id
    keys = sess.query(Key).filter(Key.chan_id == channel_id).order_by(desc(Key.created)).all()
    rights = [perm_formatter(k) for k in keys]

    form_mixin = CreateMixin()
    form_mixin.channel.data = channel_id
    mixin_out = (sess.query(Channel).filter(Channel.id == id_chan).first() for id_chan in chan.mixins())
    mixin_in: Iterable[Channel] = sess.query(Channel)\
        .filter(Channel.forwards.like(f"%{chan.id}%")).all()
    print(chan.name)

    param = {"name_site": "Lithium MQ", "title": f"Settings for {chan.name}",
             "form_main_settings": form_main_settings, "form_keys": form_keys,
             "chan": chan, "keys": keys, "rights": rights,
             "form_mixin": form_mixin, "mixin_in": mixin_in, "mixin_out": mixin_out}

    return render_template("settings.html", **param)


@app.route("/do/settings", methods=("POST",))
@login_required
def do_settings():
    form = MainSettingsChannelForm()
    if not form.validate():
        return redirect("/?error=bad_request")

    channel_id = form.id.data
    sess = SessObject()

    chan = sess.query(Channel).filter(Channel.id == channel_id).first()
    if not chan:
        return redirect("/?error=channel_invalid")

    if chan.owner_id != current_user.id:
        return redirect("/?error=no_access_to_this_channel")

    chan.name = form.name.data
    chan.is_active = form.is_active.data
    sess.commit()
    return redirect(f"/settings/{channel_id}")


@app.route("/do/create_mixin", methods=("POST",))
@login_required
def do_create_mixin():
    print(request.form)
    channel: str = request.form["channel"]
    mix_key: str = request.form["key"]
    sess = SessObject()

    chan: Channel = sess.query(Channel).filter(Channel.id == channel).first()
    if chan is None or chan.owner_id != current_user.id:
        return redirect("/?error=channel_invalid")

    key: Key = sess.query(Key).filter(Key.key == mix_key).first()
    if key is None:
        return redirect("/?error=channel_invalid")
    if key.chan_id == chan.id:
        return redirect("/?error=mixin_with_same_channel")

    # Resolve source
    src_chan: Channel = sess.query(Channel).filter(Channel.id == key.chan_id).first()

    mixins = list(src_chan.mixins())
    if chan.id in mixins:
        return redirect("/?error=already_mixed")
    mixins.append(channel)
    print(mixins)
    src_chan.update_mixins(mixins)

    sess.commit()

    return redirect(f"/settings/{channel}#list-mixin-settings-open")


@app.route("/helpdesk")
def helpdesk():
    return render_template("helpdesk.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == "__main__":
    app.run(port=8077, host="0.0.0.0")
