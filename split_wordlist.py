#!/usr/bin/env python2
# coding=utf-8
"""
Split Wordlist
"""
from __future__ import unicode_literals
from __future__ import absolute_import
import argparse
from tqdm import tqdm
import codecs
import os

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2016, summer.ai"
__date__ = "2016-01-01"
__email__ = "manuel@summer.ai"


def split_wordlist(filename, batch_size, offset=0, limit=-1):
    key = os.path.split(filename)[-1].split(".")[0]
    with codecs.open(filename, encoding='utf-8') as f:
        wordlist = f.read().splitlines()
    start_idx = list(range(len(wordlist))[offset:limit:batch_size])

    for idx in tqdm(start_idx, total=len(start_idx), desc="Saving batches", unit="batch"):
        with codecs.open("{}.{}.{}.wordlist".format(key, idx, idx + batch_size), 'w', encoding='utf-8') as f:
            print("{}.{}.{}.wordlist".format(key, idx, idx + batch_size))
            f.write("\n".join(wordlist[idx:idx + batch_size]))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Splits wordlist into batches')
    parser.add_argument('wordlist', help='Word or wordlist to add')
    parser.add_argument('--batch_size', dest='batch_size', type=int, default=0, help='Batch size of wordlist')
    parser.add_argument('--offset', dest='offset', type=int, default=0, help='Start of wordlis')
    parser.add_argument('--limit', dest='limit', type=int, default=-1, help='End of wordlist')
    args = parser.parse_args()
    split_wordlist(args.wordlist, args.batch_size, args.offset, args.limit)
