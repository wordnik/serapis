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
from serapis.config import update_config
from serapis import util

tasks_map = {}


def add(word):
    from serapis import tasks
    message = {'word': word, 'hashslug': util.hashslug(word)}
    tasks.write_message('search', message)
    print("Added task '{}'".format(message['hashslug']))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add a new word to the pipeline')
    parser.add_argument('word', help='Word to add')
    parser.add_argument('--config', dest='config', default="default", help='Config file to use')
    args = parser.parse_args()
    update_config(args.config)
    add(args.word)
