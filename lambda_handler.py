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

from serapis.config import config
config.load()  # Needs to be loaded before we import tasks
from serapis import tasks

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


def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        print(json.dumps(event))
        key = key.replace("%3A", ":")  # That's my URLDeode.
        task, _, _ = key.split(":")
        contents = s3.Object(bucket, key).get()
        print(contents)
        message = json.loads(contents['Body'].read())

        # Execute task
        tasks_map[task](message)
