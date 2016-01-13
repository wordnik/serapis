#!/usr/bin/env python2
# coding=utf-8
"""
AWS Lambda Handler
"""
from __future__ import unicode_literals
from __future__ import absolute_import

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-09"
__email__ = "manuel@summer.ai"

import boto3
import json

from serapis import tasks
from serapis.config import config
from serapis.qualify_word import clean_and_qualify
from serapis.util import hashslug

import nltk
nltk.data.path.append("nltk_data/")

print(json.dumps(config.keys))

if "aws_access_key" in config.credentials:
    s3 = boto3.resource(
        's3',
        region_name=config.region,
        aws_access_key_id=config.credentials['aws_access_key'],
        aws_secret_access_key=config.credentials['aws_access_secret']
    )
else:
    s3 = boto3.resource('s3', region_name=config.region)

tasks_map = {
    "search": tasks.search,
    "detect": tasks.detect,
    "rate": tasks.rate,
    "save": tasks.save
}


def run_task(bucket, key):
    task, _, _ = key.split(":")
    contents = s3.Object(bucket, key).get()
    print(contents)
    message = json.loads(contents['Body'].read())
    tasks_map[task](message)


def add_words(bucket, key):
    contents = s3.Object(bucket, key).get()
    words = contents['Body'].read().splitlines()
    added, skipped = set(), []
    for term in words:
        term = clean_and_qualify(term)
        if term:
            slug = hashslug(term)
            if slug not in added:
                added.add(slug)
                message = {'word': term, 'hashslug': slug}
                tasks.write_message('search', message)
            else:
                skipped.append(term)
        else:
            skipped.append(term)
    print "Added {} terms, skipped {}".format(len(added), len(skipped))


def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        print(json.dumps(event))
        key = key.replace("%3A", ":")  # That's my URLDecode.
        if key.count(":") == 2:
            return run_task(bucket, key)
        elif key.endswith(".wordlist"):
            return add_words(bucket, key)
        else:
            print "Don't know what to do with '{}'".format(key)
