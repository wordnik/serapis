#!/usr/bin/env python2
# coding=utf-8
"""
Setup
"""

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-19"
__email__ = "manuel@summer.ai"

import boto3
from config import config
import argparse


def set_up_buckets():
    s3 = boto3.resource('s3', region_name=config.region)
    existing_buckets = [bucket.name for bucket in s3.buckets.all()]
    if config.bucket not in existing_buckets:
        print("Creating bucket '{}'".format(config.bucket))
        s3.create_bucket(Bucket=config.bucket)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Set up buckets')
    parser.add_argument('--config', dest='config', default="default", help='Config file to use')
    args = parser.parse_args()
    config.load(args.config)
    set_up_buckets()
