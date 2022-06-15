from available_langs import AVAILABLE_DICTS, DEFAULT_CODE


def get_lang(lang_code: str):
    if lang_code in AVAILABLE_DICTS:
        return AVAILABLE_DICTS[lang_code]

    return AVAILABLE_DICTS[DEFAULT_CODE]
