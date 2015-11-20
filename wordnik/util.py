#!/usr/bin/env python2
# coding=utf-8
"""
Utility belt
"""
from __future__ import unicode_literals
from __future__ import absolute_import

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-09"
__email__ = "manuel@summer.ai"

import slugify
import hashlib


def singleton(class_):
    """Singleton decorator"""
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


def hashslug(word):
    """returns a slug and a short hash for a word, separated by a colon. EG

        >>> hashslug("L'esprit de l'escalier")
        'lesprit-de-lescalier:6ad283'

    """
    if not isinstance(word, unicode):
        word = word.decode('utf-8')
    return "{}:{}".format(
        slugify.slugify(word),
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
