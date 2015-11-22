#!/usr/bin/env python2
# coding=utf-8
"""
Word adder
"""
from __future__ import unicode_literals
from __future__ import absolute_import

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-09"
__email__ = "manuel@summer.ai"

import argparse
from wordnik.config import config
from wordnik import util

tasks_map = {}


def add(word):
    from wordnik import tasks
    message = {'word': args.word, 'hashslug': util.hashslug(args.word)}
    tasks.write_message('search', message)
    print("Added task '{}'".format(message['hashslug']))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add a new word to the pipeline')
    parser.add_argument('word', help='Word to add')
    parser.add_argument('--config', dest='config', default="default", help='Config file to use')
    args = parser.parse_args()
    config.load(args.config)
    add(args.word)
