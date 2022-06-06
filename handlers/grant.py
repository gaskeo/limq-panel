#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


from datetime import datetime
from enum import Enum
from typing import ClassVar, TypedDict, NamedTuple, Literal

from flask import Blueprint, render_template, redirect, request, abort, \
    make_response, jsonify
from flask_login import current_user, login_required

from forms import CreateKeyForm, GetKeysForm
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
    perm: int
    created: str


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
                   perm=key.perm,
                   created=str(key.created.date()))


def create_handler(sess_cr: ClassVar) -> Blueprint:
    """
    A closure for instantiating the handler that maintains keys creating processes.
    Must borrow a SqlAlchemy session creator for further usage.
    :param sess_cr: sqlalchemy.orm.sessionmaker object
    :return Blueprint object
    """

    app = Blueprint("grant", __name__)

    @app.route("/grant")
    @login_required
    def grant():
        f = CreateKeyForm()
        uid = current_user.id
        sess = sess_cr()

        channels = sess.query(Channel).filter(
            Channel.owner_id == uid).all()

        return render_template("create_key.html", form=f,
                               channels=channels)

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
        if error_message != ChannelMessage.Ok:
            return abort(make_response({'message': error_message}, 401))

        keys = session.query(Key). \
            filter(Key.chan_id == channel_id).all()

        keys_json = []
        for key in keys:
            keys_json.append(get_json_key(key))

        return jsonify(keys_json)

    return app
