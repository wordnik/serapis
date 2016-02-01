#!/usr/bin/env python2
# coding=utf-8
"""
Config Handler
"""

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-09"
__email__ = "manuel@summer.ai"

import boto3
import os
from util import AttrDict

path = os.path.dirname(os.path.abspath(__file__))


def load_yaml(filename):
    """
    This is a shitty YAML parser. If we were grown ups, we'd use PyYaml of course.
    But since PyYaml refuses to run on AWS Lambda, we'll do this instead.

    Args:
        filename - filename to load
    Returns:
        dict
    """
    def parse_value(value):
        if "#" in value:
            value = value[:value.index("#")]
        value = value.strip(" \n")
        if not value:
            return None
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        try:
            return int(value)
        except:
            try:
                return float(value)
            except:
                return value
    result = {}
    current_key = None
    with open(filename) as f:
        for line in f.readlines():
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                current_key = key
                result[key] = parse_value(value)
            elif line.strip().startswith("-"):
                value = line.strip(" -\n")
                if not isinstance(result[current_key], list):
                    result[current_key] = [parse_value(value)]
                else:
                    result[current_key].append(parse_value(value))
    return result


def abs_path(filename):
    return os.path.join(path, "config", "{}.yaml".format(filename))


def load_config(config):
    keys = load_yaml(abs_path("default"))

    keys['credentials'] = {}
    if os.path.exists(abs_path("credentials")):
        keys['credentials'] = load_yaml(abs_path("credentials"))
    
    if config != 'default':
        keys.update(load_yaml(abs_path(config)))

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
    config.__data.update(load_yaml(abs_path(config_name)))
