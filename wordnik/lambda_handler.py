#!/usr/bin/env python2
# coding=utf-8
"""
Searcher
"""
from __future__ import unicode_literals
from __future__ import absolute_import

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-09"
__email__ = "manuel@summer.ai"

import boto3
import json
from config import config
config.load()  # Needs to be loaded before we import tasks
import tasks


s3 = boto3.resource('s3', region_name=config.region)

tasks_map = {
    "search": tasks.search,
    "detect": tasks.detect,
    "rate": tasks.rate,
    "save": tasks.save
}


def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        task, _, _ = key.split(":")
        message = json.loads(s3.Object(bucket, key).get()['Body'].read())

        # Execute task
        tasks_map[task](message)
