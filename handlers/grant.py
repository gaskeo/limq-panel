#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


from datetime import datetime
from enum import Enum
from typing import ClassVar, TypedDict, NamedTuple, Literal

from flask import Blueprint, request, abort, \
    make_response, jsonify
from flask_login import current_user, login_required

from forms import CreateKeyForm, ToggleKeyActiveForm
from handlers.settings import confirm_channel, ChannelMessage
from storage.channel import Channel
from storage.key import Key
from storage.keygen import generate_key


class FormMessage(Enum):
    Ok = ""
    NameError = "Bad key name"
    LongNameError = "Key name too long"
    PermissionsError = "Wrong permissions"


def confirm_form(form: CreateKeyForm) -> FormMessage:
    if not form.name.data:
        return FormMessage.NameError.value
    if len(form.name.data) > 50:
        return FormMessage.LongNameError.value

    if form.permissions.data not in "01":
        return FormMessage.PermissionsError.value

    return FormMessage.Ok.value


class KeyJson(TypedDict):
    key: str
    name: str
    channel: str
    read: int
    write: int
    created: str
    active: bool
    info: bool


class KeyPermission(NamedTuple):
    can_read: int = 0
    can_write: int = 1


def get_permission(perm: Literal['0'] or Literal['1']) -> KeyPermission:
    read = perm == "0"
    write = read ^ 1
    return KeyPermission(can_read=read, can_write=write)


def get_json_key(key: Key) -> KeyJson:
    return KeyJson(key=key.key,
                   name=key.name,
                   read=key.can_read(),
                   write=key.can_write(),
                   created=str(key.created.date()),
                   active=key.active(),
                   info=key.info_allowed(),
                   channel=key.chan_id)


def create_handler(sess_cr: ClassVar) -> Blueprint:
    """
    A closure for instantiating the handler
    that maintains keys creating processes.
    Must borrow a SqlAlchemy session creator for further usage.
    """

    app = Blueprint("grant", __name__)

    @app.route("/do/grant", methods=["POST"])
    @login_required
    def do_grant():
        form = CreateKeyForm(request.form)

        error_message = confirm_form(form)
        if error_message != FormMessage.Ok.value:
            return abort(make_response({'message': error_message}, 400))

        session = sess_cr()

        channel_id = form_channel_id = form.id.data

        channel: Channel = session.query(Channel). \
            filter(Channel.id == channel_id).first()

        error_message = confirm_channel(channel, current_user)
        if error_message != ChannelMessage.Ok:
            return abort(make_response({'message': error_message}, 401))

        key_id = generate_key()
        key = Key(key=key_id, chan_id=form_channel_id,
                  name=form.name.data, created=datetime.now())

        perm = get_permission(form.permissions.data)

        info = form.info_allowed.data

        key.perm = info << 2 | perm.can_write << 1 | perm.can_read
        session.add(key)

        session.commit()

        return jsonify(get_json_key(key))

    @app.route("/do/get_keys", methods=["GET"])
    @login_required
    def do_get_keys():
        channel_id = request.args.get('channel_id', None)

        session = sess_cr()

        channel: Channel = session.query(Channel). \
            filter(Channel.id == channel_id).first()

        error_message = confirm_channel(channel, current_user)
        if error_message != ChannelMessage.Ok.value:
            return abort(make_response({'message': error_message}, 401))

        keys = session.query(Key). \
            filter(Key.chan_id == channel_id).all()

        keys_json = []
        for key in keys:
            keys_json.append(get_json_key(key))

        return jsonify(keys_json)

    @app.route("/do/toggle_key_active", methods=["POST"])
    @login_required
    def do_toggle_key():
        form = ToggleKeyActiveForm(request.form)

        session = sess_cr()

        key = session.query(Key)\
            .filter(Key.key == form.key.data).first()

        if not key:
            return abort(make_response({'message': 'Bad key'}, 401))

        channel = session.query(Channel).\
            filter(Channel.id == key.chan_id).first()

        error_message = confirm_channel(channel, current_user)

        if error_message != ChannelMessage.Ok.value:
            return abort(
                make_response({'message': error_message.value}, 400))

        key.toggle_active()

        session.commit()
        return jsonify(get_json_key(key))

    return app
