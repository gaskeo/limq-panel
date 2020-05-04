#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


from typing import ClassVar

from flask import Blueprint, render_template, redirect
from flask_login import current_user, login_required
from sqlalchemy import desc

from forms import CreateKeyForm, CreateMixinForm, MainSettingsChannelForm, RestrictMxForm
from storage.channel import Channel
from storage.key import Key


def perm_formatter(k: Key) -> str:
    r, w = k.can_read(), k.can_write()
    if r:
        return f"Приём, создан {k.created.date()}"
    if w:
        return f"Отправка, создан {k.created.date()}"
    return f"Прав доступа не установлено создан {k.created.date()}"


def create_handler(sess_cr: ClassVar) -> Blueprint:
    app = Blueprint("settings", __name__)

    @app.route("/settings/<channel_id>", methods=("GET", "POST"))
    @login_required
    def settings(channel_id):
        sess = sess_cr()
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

        form_mixin = CreateMixinForm()
        form_mixin.channel.data = channel_id

        form_mixin_restrict = RestrictMxForm()

        mixin_out = tuple(sess.query(Channel).filter(Channel.id == id_chan).first() for id_chan in chan.mixins())
        mixin_in = tuple(sess.query(Channel).filter(Channel.forwards.like(f"%{chan.id}%")).all())

        param = {"name_site": "Lithium MQ",
                 "form_main_settings": form_main_settings, "form_keys": form_keys,
                 "chan": chan, "keys": keys, "rights": rights,
                 "form_mixin": form_mixin, "mixin_in": mixin_in,
                 "mixin_out": mixin_out, "mixin_restrict": form_mixin_restrict}

        return render_template("settings.html", **param)

    @app.route("/do/settings", methods=("POST",))
    @login_required
    def do_settings():
        form = MainSettingsChannelForm()
        if not form.validate():
            return redirect("/?error=bad_request")

        channel_id = form.id.data
        sess = sess_cr()

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
        form = CreateMixinForm()
        channel: str = form.channel.data
        mix_key: str = form.key.data
        sess = sess_cr()

        chan: Channel = sess.query(Channel).filter(Channel.id == channel).first()
        if chan is None or chan.owner_id != current_user.id:
            return redirect("/?error=channel_invalid")

        key: Key = sess.query(Key).filter(Key.key == mix_key).first()
        if key is None:
            return redirect("/?error=channel_invalid")
        if key.chan_id == chan.id:
            return redirect("/?error=mixin_with_same_channel")

        if not key.can_read():
            return redirect("/?error=wrong_permissions")

        # Resolve source
        src_chan: Channel = sess.query(Channel).filter(Channel.id == key.chan_id).first()

        mixins = list(src_chan.mixins())
        if chan.id in mixins:
            return redirect("/?error=already_mixed")
        mixins.append(channel)
        src_chan.update_mixins(mixins)

        sess.commit()

        return redirect(f"/settings/{channel}#list-mixin-settings-open")

    return app
