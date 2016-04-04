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


def print_stats():
    keys = set()
    for obj in config.s3.Bucket(config.result_bucket).objects.all():
        keys.add(obj.key)
    words = [key.split(":")[0] for key in keys]
    word_set = set(words)
    print("   {} results for {} words ({:.2} FRDs / Word)".format(len(keys), len(word_set), 1.0 * len(keys) / len(word_set)))
    buckets = [0] * 15
    for word in word_set:
        buckets[min(words.count(word) - 1, 14)] += 1
    for idx, b in enumerate([60.0 * b / max(buckets) for b in buckets]):
        print "{:2} {:<60} {}".format(idx + 1, "#" * int(b), buckets[idx])

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
    if args.word == "stats":
        print_stats()
    elif args.word.endswith(".wordlist") or args.word.endswith(".txt"):
        add_wordlist(args.word, args.batch_size, args.interval)
    else:
        add(args.word)
