#!/usr/bin/env python2
# coding=utf-8
"""
Config Handler
"""

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-09"
__email__ = "manuel@summer.ai"

import argparse
from config import config
import json
import util
import os


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Set up buckets')
    parser.add_argument('word', help='Word to use')
    parser.add_argument('--config', dest='config', default="default", help='Config file to use')
    args = parser.parse_args()
    config.load(args.config)

    import tasks
    if not os.path.exists(config.local_s3):
        os.mkdir(config.local_s3)

    message = {'word': args.word, 'hashslug': util.hashslug(args.word)}
    message = tasks.search(message)
    message = tasks.detect(message)
    message = tasks.rate(message)
    message = tasks.save(message)

    print(json.dumps(message, indent=2))
