#!/usr/bin/env python2
# coding=utf-8
"""
Config Handler
"""

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-09"
__email__ = "manuel@summer.ai"

import yaml
import boto3
import os
from util import AttrDict

path = os.path.dirname(os.path.abspath(__file__))


def abs_path(filename):
    return os.path.join(path, "config", "{}.yaml".format(filename))


def load_config(config):
    with open(abs_path("default")) as c:
        keys = yaml.load(c)

    keys['credentials'] = {}
    if os.path.exists(abs_path("credentials")):
        with open(abs_path("credentials")) as c:
            keys['credentials'] = yaml.load(c) or {}
    
    if config != 'default':
        with open(abs_path(config)) as c:
            keys.update(yaml.load(c))

    if "aws_access_key" in keys['credentials']:
        keys['s3'] = boto3.resource(
            's3',
            region_name=keys['region'],
            aws_access_key_id=keys['credentials']['aws_access_key'],
            aws_secret_access_key=keys['credentials']['aws_access_secret']
        )
    else:
        keys['s3'] = boto3.resource('s3', region_name=keys['region'])

    return AttrDict(keys)


config = load_config(os.environ.get('WORDNIK_CONFIG', 'default'))


def update_config(config_name):
    global config
    with open(abs_path(config_name)) as c:
        config.__data.update(yaml.load(c))
