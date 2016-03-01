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
from serapis.config import config
from serapis.search import search_all
from serapis.save import save_all
from serapis.features import match_wordnik_rules
from serapis.annotate import batch_tag_sentences, readability_score
from serapis.persist_model import PackagedPipeline
from serapis.util import now
import numpy as np
import codecs


def write_message(task, message):
    """Writes a task with a message to the S3 bucket.
    The key will have the format task:slug:hash, e.g.

        search:lesprit-de-lescalier:6ad283
    """
    key = "{}:{}".format(task, message['hashslug'])
    if config.save_messages:
        config.s3.Object(config.bucket, key).put(Body=json.dumps(message))
    else:
        with codecs.open(os.path.join(config.local_s3, key), 'w', 'utf-8') as f:
            json.dump(message, f, indent=2)
    return message


def search(message):
    """Takes a message that must contain at least a word, searches for the word
    and saves a new message with a detect task. The incoming message is expected
    to look at least like this:

        {
            'word': ...
            'hashslug': ...
        }

    Where doc contains the parsed body text.

    Args:
        message: dict --  A message dictionary
    Returns:
        dict -- A message dictionary
    """
    word = message['word']
    message['urls'] = search_all(word)
    message['crawl_date'] = now()
    return write_message('detect', message)


def detect(message):
    """Takes a message that must contain a list of URL objects, each having
    at least a doc property. This will split the doc of each URL into
    sentences, and  determine whether each sentence is an FRD or not.
    """
    batch_tag_sentences(message)

    # Load Models
    model_pipeline = PackagedPipeline().get()
    git_hash = model_pipeline.metadata['git_hash']
    created_at = model_pipeline.metadata['created_at']

    feature_union = model_pipeline._feature_union
    model = model_pipeline._pipeline
    class_idx = np.where(model.classes_ == 1)[0][0]  # index of '1' pred in .predict_proba

    for url_object in message['urls']:
        readability_score(url_object)
        for sentence in url_object['sentences']:
            sentence_clean = sentence['s_clean']
            sentence_feature_union = feature_union.transform({
                's_clean': sentence['s_clean'],
                'pos': sentence['pos_tags']
            })

            # metadata
            sentence['model_creation_date'] = created_at
            
            # predictions from model
            sentence['patterns'] = match_wordnik_rules(sentence_clean)
            sentence['frd'] = model.predict(sentence_vec)[0]
            sentence['frd_likelihood'] = round(model.predict_proba(sentence_vec)[0][class_idx], 4)  # P(Classification as FRD)

    return write_message('save', message)


def save(message):
    """
    Saves all words to the result bucket.
    """
    save_all(message)
    return message
