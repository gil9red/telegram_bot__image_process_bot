#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import os


TOKEN = os.environ.get('TOKEN') or open('TOKEN.txt', encoding='utf-8').read().strip()

DIR_IMAGES = 'images'
