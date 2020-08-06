#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import functools


def _(text_id: str, *args) -> str:
    return TEXT[text_id][LANG].format(*args)


def set_lang(lang: str):
    global LANG
    if not lang or lang == LANG:
        return
    LANG = lang


def get_lang() -> str:
    return LANG


def reset_lang():
    set_lang(DEFAULT_LANG)


def update_lang(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        update = args[0]
        if update.effective_user:
            language_code = update.effective_user.language_code
            if language_code != 'ru':
                language_code = 'en'
            set_lang(language_code)
        return func(*args, **kwargs)
    return wrapper


TEXT = {
    'WELCOME_MESSAGE': {
        'ru': 'Отправь мне картинку',
        'en': 'Send me a picture',
    },
    'UNKNOWN_COMMAND': {
        'ru': 'Неизвестная команда: {}',
        'en': 'Unknown command: {}',
    },
    'NEED_TO_SEND_PICTURE': {
        'ru': 'Нужно отправить мне картинку',
        'en': 'Need to send me a picture',
    },
    'ERROR_TEXT': {
        'ru': '⚠ Возникла какая-то проблема. Попробуйте повторить запрос или попробовать чуть позже ...',
        'en': '⚠ There is a problem. Please try again or try a little later ...',
    },
    'DOWNLOADING_PICTURE': {
        'ru': 'Скачиваю картинку ...',
        'en': 'Downloading a picture ...',
    },
    'PICTURE_DOWNLOADED': {
        'ru': 'Картинка скачана!',
        'en': 'Picture downloaded!',
    },
    'COMMANDS_ARE_NOW_AVAILABLE': {
        'ru': 'Теперь доступны команды над картинкой!',
        'en': 'Commands above the picture are now available!',
    },
}

DEFAULT_LANG = 'en'
LANG = DEFAULT_LANG
