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
from util import singleton

path = os.path.dirname(os.path.abspath(__file__))


def abs_path(filename):
    return os.path.join(path, "config", "{}.yaml".format(filename))


@singleton
class Config(object):
    """
    Singleton config object. Usage:

    >>> from config import config  # Wherever you need it

    This loads the default config. To override this, you can either set the
    $WORDNIK_CONFIG environment variable to e.g. 'dev' to override the default
    config with the contents of confif/dev.yaml, or override it later by
    calling

    >>> config.load('dev'
    """
    keys = {}
    config = None

    @property
    def s3(self):
        if self._s3:
            return self._s3

        if "aws_access_key" in self.credentials:
            self._s3 = boto3.resource(
                's3',
                region_name=self.region,
                aws_access_key_id=self.credentials['aws_access_key'],
                aws_secret_access_key=self.credentials['aws_access_secret']
            )
        else:
            self._s3 = boto3.resource('s3', region_name=self.region)

        return self._s3
    
    def __getattr__(self, key):
        if not self.config:
            raise RuntimeError("Config is not loaded yet.")
        return self.keys[key]

    def __init__(self, config='default'):
        self.config = config
        self._s3 = None
        with open(abs_path("default")) as c:
            self.keys = yaml.load(c)

        self.keys['credentials'] = {}
        if os.path.exists(abs_path("credentials")):
            with open(abs_path("credentials")) as c:
                self.keys['credentials'] = yaml.load(c) or {}
        
        self.load(config)

    def load(self, config="default"):
        if config != 'default':
            with open(abs_path(config)) as c:
                self.keys.update(yaml.load(c))

config = Config(os.environ.get('WORDNIK_CONFIG', 'default'))
