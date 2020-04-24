#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


from flask import Flask, render_template, redirect, request, make_response, abort
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

from storage.user import User
from storage.channel import Channel
from storage.key import Key
from storage.db_session import base_init
from storage.keygen import chan_identifier, generate_key

from forms import RegisterForm, RegisterChannelForm, LoginForm, CreateKeyForm, \
    MainSettingsChannelForm

from errors import explain as explain_error

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


@app.route("/do/create_channel", methods=("POST", ))
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


@app.route("/do/grant", methods=("POST", ))
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
    key = Key(key=key_s, chan_id=channel, name=form.name.data)

    read = form.read.data
    write = form.write.data

    key.perm = write << 1 | read
    sess.add(key)

    sess.commit()

    return redirect(f"/settings/{channel}#list-key-open")


# tmp
def perm_formatter(k: Key) -> str:
    r, w = k.can_read(), k.can_write()
    if r and w:
        return "Приём, отправка"
    if r:
        return "Приём"
    if w:
        return "Отправка"
    return "Прав доступа не установлено"


@app.route("/settings/<channel_id>", methods=("GET", "POST"))
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
    keys = sess.query(Key).filter(Key.chan_id == channel_id).all()[::-1]
    rights = [perm_formatter(k) for k in keys][::-1]

    param = {"name_site": "Lithium MQ", "title": f"Settings for {chan.name}",
             "form_main_settings": form_main_settings, "form_keys": form_keys,
             "chan": chan, "keys": keys, "rights": rights}

    return render_template("settings.html", **param)


@app.route("/do/settings", methods=("POST", ))
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


@app.route("/helpdesk")
def helpdesk():
    return render_template("helpdesk.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0")

