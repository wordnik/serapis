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
from parse import parse
from extract import extract
from detect import detect
from rate import rate
from save import save


def process(word: str):
    for result in search(word):
        if qualify(result):
            cleaned = parse(result)
            cleaned['word'] = word
            for sentence in extract(cleaned['body'], word):
                frd_result = cleaned.copy()
                if detect(sentence, word):
                    frd_result['sentence'] = sentence
                    frd_result['word'] = word
                    frd_result['rating'] = rate(frd_result)
                    save(frd_result)


if __name__ == "__main__":
    config.load()
    process(sys.argv[1])
