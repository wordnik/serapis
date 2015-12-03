#!/usr/bin/env python2
# coding=utf-8
"""
Task dispatcher
"""
from __future__ import unicode_literals
from __future__ import absolute_import

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-20"
__email__ = "manuel@summer.ai"

import os
import json
import boto3
from textblob import TextBlob
from .config import config
from . import search as search_helper

if "aws_access_key" in config.credentials:
    s3 = boto3.resource(
        's3',
        region_name=config.region,
        aws_access_key_id=config.credentials['aws_access_key'],
        aws_secret_access_key=config.credentials['aws_access_secret']
    )
else:
    s3 = boto3.resource('s3', region_name=config.region)


def write_message(task, message):
    """Writes a task with a message to the S3 bucket.
    The key will have the format task:slug:hash, e.g.

        search:lesprit-de-lescalier:6ad283
    """
    key = "{}:{}".format(task, message['hashslug'])
    if config.save_messages:
        s3.Object(config.bucket, key).put(Body=json.dumps(message))
    else:
        with open(os.path.join(config.local_s3, key), 'w') as f:
            json.dump(message, f)
    return message


def search(message):
    """Takes a message that must contain at least a word, searches for the word
    and saves a new message with a detect task. The incoming message is expected
    to look at least like this:

        {
            'word': ...
            'hashslug': ...
        }

    The message saved will look like this:

        {
            word: ...
            'hashslug': ...
            urls: [
                {
                    url: ...
                    author: ...
                    date: ...
                    doc: ...
                },
                ...
            ]
        }

    Where doc contains the parsed body text.

    Args:
        message: dict --  A message dictionary
    Returns:
        dict -- A message dictionary
    """
    word = message['word']
    message['urls'] = search_helper.search_diffbot_cache(word)
    return write_message('detect', message)


def detect(message):
    """Takes a message that must contain a list of URL objects, each having
    at least a doc property. This will split the doc of each URL into
    sentences, and  determine whether each sentence is an FRD or not. Finally
    it will create a 'rate' message that looks like this:

        {
            word: ...
            urls: [
                {
                    url: ...
                    author: ...
                    date: ...
                    doc: ...
                    features: { ... }
                    sentences: [
                        {
                        s: ...
                        frd: ...
                        }
                    ]
                },
                ...
            ]
        }

    Where s is the sentence and frd is the probability of this sentence being an FRD.
    """
    word = message['word']
    for url in message['urls']:
        doc = TextBlob(url['doc'])
        url['sentences'] = []
        for sentence in doc.sentences:
            if word.lower() in sentence.lower():
                result = {
                    's': str(sentence),
                    'frd': 0  # Detect if this is an FRD
                }
                url['sentences'].append(result)
    return write_message('rate', message)


def rate(message):
    """
    ...
    """
    for url in message['urls']:
        for sentence in url['sentences']:
            sentence['rating'] = 0
    return write_message('save', message)


def save(message):
    """
    ...
    """
    if not config.save_messages:
        # Write things locally!
        resultfile = os.path.join(config.local_s3_results, message['hashslug'])
        with open(resultfile, 'w') as f:
            print("Saving results to '{}".format(resultfile))
            json.dump(message, f)
    else:
        # Just save it to the logs
        print(json.dumps(message))
    return message
