#!/usr/bin/env python2
# coding=utf-8
"""
Utility belt
"""

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-09"
__email__ = "manuel@summer.ai"


def singleton(class_):
    """Singleton decorator"""
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


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
