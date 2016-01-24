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
from serapis.config import update_config, config
from serapis import util

tasks_map = {}


def add(word):
    from serapis import tasks
    message = {'word': word, 'hashslug': util.hashslug(word)}
    tasks.write_message('search', message)
    print("Added task '{}'".format(message['hashslug']))


def add_wordlist(filename):
    import os
    key = os.path.split(filename)[-1]
    config.s3.Object(config.bucket, key).put(Body=open(filename, 'rb'))
    print("Added wordlist '{}'".format(key))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add a new word to the pipeline')
    parser.add_argument('word', help='Word or wordlist to add')
    parser.add_argument('--config', dest='config', default="default", help='Config file to use')
    args = parser.parse_args()
    update_config(args.config)
    if args.word.endswith(".wordlist"):
        add_wordlist(args.word)
    else:
        add(args.word)
