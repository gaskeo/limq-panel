#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\


from typing import Optional

ERRORS = {
    "bad_request": "Что-то пошло не так",
    "channel_invalid": "Указанного канала не существует",
    "no_access_to_this_channel": "У Вас нет прав на создание ключей для этого канала",
    "mixin_with_same_channel": "Рекурсивный миксин невозможен",
    "already_mixed": "Миксин уже создан",
    "wrong_permissions": "Неверно заданы права для ключа",
}


def explain(err: str) -> Optional[str]:
    return ERRORS.get(err.lower(), None)

