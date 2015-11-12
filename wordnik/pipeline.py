#!/usr/bin/env python3
# coding=utf-8
"""
Config Handler
"""

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-09"
__email__ = "manuel@summer.ai"

import sys

from config import config
from search import search
from qualify import qualify
from parse import parse_batch
from extract import extract
from detect import detect
from rate import rate
from save import save
from util import batch
from objects import Term


def process(word: str):
    frd = Term(word)
    for search_term in batch(search(frd, filter=qualify), batch_size=config.diffbot_batch_size):
        for result in parse_batch(search_term):
            # sentences containing word from cleaned body text
            for frd in extract(result):
                if detect(frd):
                    frd.rating = rate(frd)
                    # NB use min = 0 during dev
                    if frd.rating >= config.min_frd_rating:
                        save(frd)


if __name__ == "__main__":
    config.load()
    process(sys.argv[1])
