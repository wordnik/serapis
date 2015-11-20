#!/usr/bin/env python2
# coding=utf-8
"""
Task dispatcher
"""

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-20"
__email__ = "manuel@summer.ai"

import boto3
from config import config
import json
from textblob import TextBlob

s3 = boto3.resource('s3', region_name=config.region)


def write_message(task, message):
    """Writes a message to the S3 bucket."""
    if not config.save_messages:
        return
    s3.Object(config.bucket, task).put(Body=json.dumps(message))


def search(message):
    """Takes a message that must contain at least a word, searches for the word
    and saves a new message with a detect task. The incoming message is expected
    to look at least like this:

        {
            'word': ...
        }

    The message saved will look like this:

        {
            word: ...
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
    """
    message['urls'] = []
    # Search Diffbot's cache
    # if there are enough results in cache:
    #     add results to message
    # else:
    #    Search Bing
    #    Hit Diffbot's exctract API with result urls
    write_message('detect', message)


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

    for url in message['urls']:
        doc = TextBlob(url['doc'])
        url['sentences'] = []
        for sentence in doc.sentences:
            result = {
                's': sentence,
                'frd': 0  # Detect if this is an FRD
            }
            url['sentences'].append(result)
    write_message('rate', message)


def rate(message):
    """
    ...
    """
    for url in message['urls']:
        for sentence in url['sentences']:
            sentence['rating'] = 0
    write_message('save', message)


def save(message):
    """
    ...
    """
    pass
