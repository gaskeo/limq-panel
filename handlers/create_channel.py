#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\
from enum import Enum
from typing import ClassVar

from flask import Blueprint, abort, make_response, jsonify
from flask_login import current_user, login_required

from forms import RegisterChannelForm, RenameChannelForm
from storage.channel import Channel
from storage.keygen import chan_identifier

from .get_channels import get_base_json_channel


class FormMessage(Enum):
    Ok = ""
    NameError = "Bad channel name"
    LongNameError = "Channel name too long"


def confirm_form(form: RegisterChannelForm or RenameChannelForm) -> \
        FormMessage:
    if not form.name.data:
        return FormMessage.NameError.value

    if len(form.name.data) > 50:
        return FormMessage.LongNameError.value

    return FormMessage.Ok.value


def create_handler(sess_cr: ClassVar) -> Blueprint:
    """
    A closure for instantiating the handler that maintains channel creating processes.
    Must borrow a SqlAlchemy session creator for further usage.
    :param sess_cr: sqlalchemy.orm.sessionmaker object
    :return Blueprint object
    """

    app = Blueprint("create_channel", __name__)

    @app.route("/do/create_channel", methods=["POST"])
    @login_required
    def do_create_channel():
        form = RegisterChannelForm()

        error_message = confirm_form(form)
        if error_message != FormMessage.Ok.value:
            return abort(make_response({'message': error_message}, 400))

        session = sess_cr()
        channel = Channel(
            name=form.name.data,
            id=chan_identifier(),
            owner_id=current_user.id
        )

        session.add(channel)
        session.commit()
        return jsonify(get_base_json_channel(channel))

    return app
