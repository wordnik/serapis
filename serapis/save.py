#!/usr/bin/env python
# coding=utf-8
"""
Saver module
"""
from __future__ import unicode_literals
from __future__ import absolute_import
from itertools import chain
from collections import Counter

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2016, summer.ai"
__date__ = "2016-01-08"
__email__ = "manuel@summer.ai"

import os
import json
from .config import config
from .util import numeric_hash, slugify
import logging

log = logging.getLogger('serapis.save')


def collect_variants(message):
    """
    Collects all spelling variants from a message.

    Args:
        message: dict -- mssage dict with 'urls' key
    Returns:
        dict -- all spelling variants, mapped to their frequency
    """
    c = Counter(chain(*(u['variants'] for u in message['urls'])))
    total = sum(c.values(), 0.0)
    return {variant: count / total for variant, count in c.iteritems()}


def assemble_result(message, url_object, sentence):
    """
    Picks all relevant information for a single sentence to be saved
    according to https://github.com/summerAI/wordnik/wiki/Result-Format .

    Args:
        message: dict
        url_object: dict
        sentence: dict
    Returns:
        dict
    """
    return {
        "metadata":
        {
            "searchAPI": url_object.get('search_provider'),
            "source": url_object.get('source'),
            "documentTitle": url_object.get('title'),
            "crawlDate": message.get('crawl_date'),  # ISO8601
            "documentId": numeric_hash(url_object.get('url', "")),
            "readability": url_object.get('readability_score')
        },
        "pub_date": url_object.get('pub_date'),
        "author": url_object.get('author'),
        "exampleType": sentence.get('type', 'frd'),
        "rating": sentence.get('rating'),
        "url": url_object.get('url'),
        "word": message.get('word'),
        "wordVariants": message.get('variants'),
        "text": sentence.get('s'),
        "frd_rating": sentence.get('frd'),
        "exampleId": numeric_hash(sentence.get('s', ""))
    }
    

def save_all(message):
    message['variants'] = collect_variants(message)
    for url_object in message['urls']:
        for sentence in url_object['sentences']:
            if sentence.get('frd', 0) >= config.min_frd_prob:
                result = assemble_result(message, url_object, sentence)
                save_single(result)


def save_single(result):
    """
    Saves a single result object locally or on S3 and ElasticSearch

    Args:
        result: dict -- Compliant with https://github.com/summerAI/wordnik/wiki/Result-Format
    """
    result_slug = "{}:{}".format(slugify(result['word']), result['exampleId'])
    if not config.save_messages:
        # Write things locally!
        resultfile = os.path.join(config.local_s3_results, result_slug)
        with open(resultfile, 'w') as f:
            log.info("Saving results to '{}".format(resultfile))
            json.dump(result, f, indent=2)
    else:
        config.s3.Object(config.bucket, result_slug).put(Body=json.dumps(result))
        if result['rating'] > config.min_frd_rating:
            # @TODO save to ElasticSearch
            pass
