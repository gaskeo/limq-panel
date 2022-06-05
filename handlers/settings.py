#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\
from enum import Enum
from typing import ClassVar

from flask import Blueprint, redirect, abort, \
    make_response, jsonify
from flask_login import current_user, login_required

from forms import CreateKeyForm, CreateMixinForm, RenameChannelForm, \
    RestrictMxForm
from storage.channel import Channel
from storage.key import Key
from storage.user import User

from .create_channel import confirm_form, FormMessage
from .get_channels import get_json_channel


def perm_formatter(k: Key) -> str:
    r, w = k.can_read(), k.can_write()
    if r:
        return f"Приём, создан {k.created.date()}"
    if w:
        return f"Отправка, создан {k.created.date()}"
    return f"Прав доступа не установлено создан {k.created.date()}"


class ChannelMessage(Enum):
    Ok = ""
    ChannelNotExistError = "Channel doesn't exist"
    NotOwnerError = "You aren't owner of this channel"


def confirm_channel(channel: Channel or None, user: User) -> ChannelMessage:
    if not channel:
        return ChannelMessage.ChannelNotExistError
    if channel.owner_id != user.id:
        return ChannelMessage.NotOwnerError
    return ChannelMessage.Ok


def create_handler(sess_cr: ClassVar) -> Blueprint:
    """
    A closure for instantiating the handler that maintains channel settings process.
    Must borrow a SqlAlchemy session creator for further usage.
    :param sess_cr: sqlalchemy.orm.sessionmaker object
    :return Blueprint object
    """

    app = Blueprint("settings", __name__)

    @app.route("/do/edit_channel", methods=["POST"])
    @login_required
    def do_settings():
        """ Handler for settings changing page. """

        form = RenameChannelForm()
        error_message = confirm_form(form)
        if error_message != FormMessage.Ok.value:
            return abort(make_response({'message': error_message}, 400))

        channel_id = form.id.data
        session = sess_cr()

        # Channel validation.
        channel = session.query(Channel). \
            filter(Channel.id == channel_id).first()

        error_message = confirm_channel(channel, current_user)
        if error_message != ChannelMessage.Ok:
            return abort(make_response({'message': error_message}, 401))

        channel.name = form.name.data
        session.commit()

        return jsonify(get_json_channel(channel, sess_cr()))

    @app.route("/do/create_mixin", methods=("POST",))
    @login_required
    def do_create_mixin():
        """ Handler for mixin creating. """

        form = CreateMixinForm()
        channel: str = form.channel.data
        mix_key: str = form.key.data
        sess = sess_cr()

        # Key and channel validation

        chan: Channel = sess.query(Channel).filter(
            Channel.id == channel).first()
        if chan is None or chan.owner_id != current_user.id:
            return redirect("/?error=no_access_to_this_channel")

        key: Key = sess.query(Key).filter(Key.key == mix_key).first()
        if key is None or not key.active():
            return redirect("/?error=channel_invalid")

        if key.chan_id == chan.id:
            return redirect("/?error=mixin_with_same_channel")

        if not key.can_read():
            return redirect("/?error=wrong_permissions")

        # Resolve source
        src_chan: Channel = sess.query(Channel).filter(
            Channel.id == key.chan_id).first()

        mixins = list(src_chan.mixins())
        if chan.id in mixins:
            return redirect("/?error=already_mixed")
        mixins.append(channel)
        src_chan.update_mixins(mixins)

        sess.commit()

        return redirect(f"/settings/{channel}#list-mixin-settings-open")

    return app
