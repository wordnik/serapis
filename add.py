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
import codecs
from serapis.config import update_config, config
from serapis import util
from serapis import preprocess
import os
import time
from tqdm import tqdm
import math

tasks_map = {}


def add(word):
    """
    Adds a single word to the pipeline.
    """
    from serapis import tasks
    message = {'word': word, 'hashslug': util.hashslug(word)}
    tasks.write_message('search', message)
    print("Added task '{}'".format(message['hashslug']))


def add_wordlist(filename, batch_size=0, interval=60):
    """
    Adds a wordlist to the pipeline.

    Args:
        filename: str -- file with one term per line
        batch_size: int -- if non-zero, chop wordlist into chunks and add one
                    at time
        interval: int -- if non-zero, wait for n seconds between each batch
    """
    key = os.path.split(filename)[-1].split(".")[0]
    with codecs.open(filename, 'r', 'utf-8') as f:
        wordlist = f.read().splitlines()
    cleaned = list(tqdm(preprocess.clean_and_qualify_wordlist(wordlist), total=len(wordlist) * .6, desc="Cleaning", unit="word"))
    print "Retained {} out of {} words ({:.0%}).".format(len(cleaned), len(wordlist), 1. * len(cleaned) / len(wordlist))
    if not batch_size:
        config.s3.Object(config.bucket, key + ".wordlist").put(Body="\n".join(cleaned))
    else:
        batches = int(math.ceil(1. * len(cleaned) / batch_size))
        key_ext = 0
        for sublist in tqdm(util.batch(cleaned, batch_size), total=batches, desc="Uploading batches", unit="batch"):
            config.s3.Object(config.bucket, "{}.{}.wordlist".format(key, key_ext)).put(Body="\n".join(sublist))
            key_ext += 1
            time.sleep(interval)
    print("Added wordlist '{}'".format(key))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add a new word to the pipeline')
    parser.add_argument('word', help='Word or wordlist to add')
    parser.add_argument('--config', dest='config', default="default", help='Config file to use')
    parser.add_argument('--batch_size', dest='batch_size', type=int, default=0, help='Batch size of wordlist')
    parser.add_argument('--interval', dest='interval', type=int, default=60, help='Batch size of wordlist')
    parser.add_argument('--offset', dest='offset', type=int, default=0, help='Start of wordlis')
    parser.add_argument('--limit', dest='limit', type=int, default=0, help='End of wordlist')
    args = parser.parse_args()
    update_config(args.config)
    if args.word.endswith(".wordlist") or args.word.endswith(".txt"):
        add_wordlist(args.word, args.batch_size, args.interval)
    else:
        add(args.word)
