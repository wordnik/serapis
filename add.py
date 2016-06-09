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
import json

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
    if not os.path.exists("current_page.{}".format(key)):
        page = 0
    else:
        with open("current_page.{}".format(key)) as f:
            page = int(f.read())
    with codecs.open(filename, 'r', 'utf-8') as f:
        wordlist = f.read().splitlines()

    print "Continuing from page", page
    cleaned = wordlist[page:]
    if not batch_size:
        config.s3.Object(config.bucket, key + ".wordlist").put(Body="\n".join(cleaned))
    else:
        batches = int(math.ceil(1. * len(cleaned) / batch_size))
        key_ext = 0
        for sublist in tqdm(util.batch(cleaned, batch_size), total=batches, desc="Uploading batches", unit="batch"):
            if config.save_messages:
                config.s3.Object(config.bucket, "{}.{}.wordlist".format(key, key_ext)).put(Body="\n".join(sublist))
            key_ext += 1
            page += batch_size
            time.sleep(interval)
            with open("current_page.{}".format(key), 'w') as f:
                f.write(str(page))
    print("Added wordlist '{}'".format(key))


def clean(filename):
    with codecs.open(filename, 'r', 'utf-8') as f:
        wordlist = f.read().splitlines()
    cleaned = list(tqdm(preprocess.clean_and_qualify_wordlist(wordlist), total=len(wordlist) * .6, desc="Cleaning", unit="word"))
    print "Retained {} out of {} words ({:.0%}).".format(len(cleaned), len(wordlist), 1. * len(cleaned) / len(wordlist))
    print "\n".join(cleaned)


def print_stats():
    results, queries = [], set()
    for obj in config.s3.Bucket(config.result_bucket).objects.all():
        results.append(obj.key.split(":")[0])
    for obj in config.s3.Bucket(config.bucket).objects.all():
        if obj.key.startswith("search"):
            queries.add(obj.key.split(":")[1])
    result_set = set(results)
    print("   {} queries, {} words, {} FRDs ({:.2} FRDs / Word, {:.1%} of queries found)".format(
        len(queries),
        len(result_set),
        len(results),
        1.0 * len(results) / len(result_set),
        1.0 * len(result_set) / len(queries)))
    buckets = [0] * 15
    for word in result_set:
        buckets[min(results.count(word) - 1, 14)] += 1
    for idx, b in enumerate([60.0 * b / max(buckets) for b in buckets]):
        print "{:2} {:<60} {}".format(idx + 1, "█" * int(b), buckets[idx])


def print_hist(n=10000):
    results = []
    for obj in config.s3.Bucket(config.result_bucket).objects.limit(n):
        body = json.loads(obj.get()['Body'].read())
        results.append(body['frd_rating'])
    print results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add a new word to the pipeline')
    parser.add_argument('word', help='Word or wordlist to add')
    parser.add_argument('--config', dest='config', default="default", help='Config file to use')
    parser.add_argument('--batch_size', dest='batch_size', type=int, default=0, help='Batch size of wordlist')
    parser.add_argument('--interval', dest='interval', type=int, default=60, help='Batch size of wordlist')
    parser.add_argument('--offset', dest='offset', type=int, default=0, help='Start of wordlis')
    parser.add_argument('--limit', dest='limit', type=int, default=0, help='End of wordlist')
    parser.add_argument('--clean', dest='clean', type=int, default=0, help='End of wordlist')
    args = parser.parse_args()
    update_config(args.config)
    if args.word == "stats":
        print_stats()
    if args.word == "hist":
        print_hist()
    elif args.word.endswith(".wordlist") or args.word.endswith(".txt"):
        add_wordlist(args.word, args.batch_size, args.interval)
    else:
        add(args.word)
