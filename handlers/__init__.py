#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\
import string

from flask import abort, make_response


def make_abort(message='', code=400) -> abort:
    return abort(make_response({"message": message}, code))


VALID_NAME_CHARS = string.digits + string.ascii_letters + '-._'
VALID_DOMAIN_CHARS = string.digits + string.ascii_letters + '-'


def confirm_email(email: str) -> str:
    def valid_name() -> bool:
        if len(name) < 1:
            return False
        if name[-1] in '-._' or name[0] in '-._':
            return False
        if tuple(filter(
                lambda character: character not in VALID_NAME_CHARS,
                name)):
            return False

        return True

    def valid_domain() -> bool:
        if len(domain) < 1:
            return False
        if tuple(filter(
                lambda character: character not in VALID_DOMAIN_CHARS,
                domain)):
            return False

        return True

    def valid_zone() -> bool:
        if len(zone) < 1:
            return False
        if tuple(filter(
                lambda character: character not in VALID_DOMAIN_CHARS,
                zone)):
            return False

        return True

    if not email:
        return ''
    split = email.strip().split('@')
    if len(split) != 2:
        return ''
    name, full_domain = split
    domain_split = full_domain.split('.')
    if len(domain_split) != 2:
        return ''
    domain, zone = domain_split
    if not valid_name() or not valid_domain() or not valid_zone():
        return ''
    return f"{name}@{domain}.{zone}"
