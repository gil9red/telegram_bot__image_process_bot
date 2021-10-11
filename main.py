#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import io
import os
import time

from pathlib import Path

import requests

# pip install Pillow
from PIL import Image

# pip install -U python-telegram-bot
from telegram import ReplyKeyboardMarkup, ChatAction, Update
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackContext, Defaults

import config
from commands import invert, gray, invert_gray, pixelate, get_image_info, jackal_jpg, thumbnail, blur
from common import get_logger, log_func, catch_error
from i18n import _, update_lang


log = get_logger(__file__)


COMMANDS = {
    'invert': invert,
    'gray': gray,
    'invert_gray': invert_gray,
    'get_image_info': get_image_info,
    'pixelate': pixelate,
    'pixelate16': lambda img: pixelate(img, 16),
    'pixelate32': lambda img: pixelate(img, 32),
    'pixelate48': lambda img: pixelate(img, 48),
    'jackal_jpg': jackal_jpg,
    'thumbnail32': lambda img: thumbnail(img, (32, 32)),
    'thumbnail64': lambda img: thumbnail(img, (64, 64)),
    'thumbnail128': lambda img: thumbnail(img, (128, 129)),
    'blur': blur,
    'blur5': lambda img: blur(img, 5),
    'original': lambda img: img
}
BUTTON_LIST = [
    ['invert', 'gray', 'invert_gray', 'jackal_jpg'],
    ['pixelate', 'pixelate16', 'pixelate32', 'pixelate48'],
    ['thumbnail32', 'thumbnail64', 'thumbnail128'],
    ['get_image_info', 'blur', 'blur5', 'original'],
]
REPLY_KEYBOARD_MARKUP = ReplyKeyboardMarkup(BUTTON_LIST, resize_keyboard=True)


def get_file_name_image(chat_id: int) -> Path:
    return config.DIR_IMAGES / f'{chat_id}.jpg'


@catch_error(log)
@update_lang
@log_func(log)
def on_start(update: Update, context: CallbackContext):
    update.effective_message.reply_text(_('WELCOME_MESSAGE'))


@catch_error(log)
@update_lang
@log_func(log)
def on_request(update: Update, context: CallbackContext):
    message = update.effective_message
    chat_id = message.chat_id
    text = message.text
    log.debug('text: %s', text)

    if text not in COMMANDS:
        message.reply_text(_('UNKNOWN_COMMAND', repr(text)))
        return

    context.bot.send_chat_action(chat_id, action=ChatAction.UPLOAD_PHOTO)

    file_name = get_file_name_image(chat_id)
    if not file_name.exists():
        message.reply_text(_('NEED_TO_SEND_PICTURE'))
        return

    img = Image.open(file_name)
    log.debug('img: %s', img)

    # Получение и вызов функции
    result = COMMANDS[text](img)

    if type(result) == str:
        log.debug('reply_text')
        message.reply_text(result, reply_markup=REPLY_KEYBOARD_MARKUP)
    else:
        log.debug('reply_photo')

        bytes_io = io.BytesIO()
        result.save(bytes_io, format='JPEG')
        bytes_io.seek(0)

        message.reply_photo(bytes_io, reply_markup=REPLY_KEYBOARD_MARKUP)


@catch_error(log)
@update_lang
@log_func(log)
def on_photo(update: Update, context: CallbackContext):
    message = update.effective_message
    chat_id = message.chat_id

    log.debug('Downloading a picture ...')
    msg = _('DOWNLOADING_PICTURE')
    progress_message = message.reply_text(msg + '\n⬜⬜⬜⬜⬜')

    context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    url = message.photo[-1].get_file().file_path
    rs = requests.get(url)

    progress_message.edit_text(msg + '\n⬛⬛⬛⬜⬜')

    file_name = get_file_name_image(chat_id)
    file_name.write_bytes(rs.content)

    log.debug('Picture downloaded!')
    msg = _('PICTURE_DOWNLOADED')
    progress_message.edit_text(msg + '\n⬛⬛⬛⬛⬛')
    progress_message.delete()

    message.reply_text(
        _('COMMANDS_ARE_NOW_AVAILABLE'),
        reply_markup=REPLY_KEYBOARD_MARKUP
    )


@catch_error(log)
@update_lang
def on_error(update: Update, context: CallbackContext):
    log.error('Error: %s\nUpdate: %s', context.error, update, exc_info=context.error)

    if update:
        update.effective_message.reply_text(_('ERROR_TEXT'))


def main():
    cpu_count = os.cpu_count()
    workers = cpu_count
    log.debug(f'System: CPU_COUNT={cpu_count}, WORKERS={workers}')

    log.debug('Start')

    updater = Updater(
        config.TOKEN,
        workers=workers,
        defaults=Defaults(run_async=True),
    )

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', on_start))
    dp.add_handler(MessageHandler(Filters.text, on_request))
    dp.add_handler(MessageHandler(Filters.photo, on_photo))

    dp.add_error_handler(on_error)

    updater.start_polling()
    updater.idle()

    log.debug('Finish')


if __name__ == '__main__':
    while True:
        try:
            main()
        except:
            log.exception('')

            timeout = 15
            log.info(f'Restarting the bot after {timeout} seconds')
            time.sleep(timeout)
