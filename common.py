#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import functools
import logging
import sys
from pathlib import Path


def get_logger(file_name: str, dir_name='logs'):
    dir_name = Path(dir_name).resolve()
    dir_name.mkdir(parents=True, exist_ok=True)

    file_name = str(dir_name / Path(file_name).resolve().name) + '.log'

    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(asctime)s] %(filename)s[LINE:%(lineno)d] %(levelname)-8s %(message)s')

    fh = logging.FileHandler(file_name, encoding='utf-8')
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(logging.DEBUG)

    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    log.addHandler(fh)
    log.addHandler(ch)

    return log


def log_func(logger: logging.Logger):
    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if args:
                update = args[0]
                if update:
                    chat_id = user_id = first_name = last_name = None

                    if update.effective_chat:
                        chat_id = update.effective_chat.id

                    if update.effective_user:
                        user_id = update.effective_user.id
                        first_name = update.effective_user.first_name
                        last_name = update.effective_user.last_name

                    msg = f'[chat_id={chat_id}, user_id={user_id}, first_name={first_name!r}, last_name={last_name!r}]'
                    logger.debug(func.__name__ + msg)

            return func(*args, **kwargs)

        return wrapper
    return actual_decorator
