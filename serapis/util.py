#!/usr/bin/env python2
# coding=utf-8
"""
Utility belt
"""
from __future__ import unicode_literals
from __future__ import absolute_import
from functools import wraps

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-09"
__email__ = "manuel@summer.ai"

import hashlib
import re
from unidecode import unidecode
import threading


class AsynchronousRequest(object):
    def __init__(self, function, *args, **kwargs):
        self.value = None
        self.error = None
        self._function = function
        self._thread = threading.Thread(target=self._fetch, args=(function,) + args, kwargs=kwargs)
        self._thread.start()

    def _fetch(self, function, *args, **kwargs):
        try:
            self.value = function(*args, **kwargs)
        except Exception, e:
            self.error = e

    @property
    def done(self):
        return not self._thread.isAlive()


def async(function, *args, **kwargs):
    return AsynchronousRequest(function, *args, **kwargs)


class Collector(object):
    """Collector decorator"""
    all = []

    def __init__(self, func):
        self.func = func
        self.all.append(func)
        wraps(func)(self)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


def singleton(cls):
    """Singleton decorator"""
    instances = {}

    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getinstance


def slugify(string):
    """
    Slugify a unicode string.

        >>> slugify(u"Héllø Wörld")
        u"hello-world"
    """
    return re.sub(r'[-\s]+', '-',
                  re.sub(r'[^\w\s-]', '', unidecode(string))
                  ).strip().lower()


def hashslug(word):
    """returns a slug and a short hash for a word, separated by a colon. EG

        >>> hashslug("L'esprit de l'escalier")
        'lesprit-de-lescalier:6ad283'

    """
    if not isinstance(word, unicode):
        word = word.decode('utf-8')
    return "{}:{}".format(
        slugify(word),
        hashlib.md5(word).hexdigest()[:6]
    )


def batch(generator, batch_size=5):
    """Wraps around a generator and yields results in batches.

    Example:

        gen = (letter for letter in string.ascii_uppercase)
        for n in batch(gen, 8):
            print(''.join(n))

    Will produce:

        ABCDEFGH
        IJKLMNOP
        QRSTUVWX
        YZ
    """
    cont = True
    while cont:
        result = []
        for n in range(batch_size):
            try:
                result.append(next(generator))
            except StopIteration:
                cont = False
                break
        yield result
