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
import os
from util import singleton


@singleton
class Config(object):
    """
    Singleton config object. Usage:

        from config import config  # Wherever you need it
        config.load('dev')  # Only once, anywhere in your code
        print(config.aws_secret_token)

    This will use the config parameters from the config/dev.yaml file, and
    fall back on config/default.yaml.
    """
    keys = {}
    config = None

    def __getattr__(self, key):
        if not self.config:
            raise RuntimeError("Config is not loaded yet.")
        return self.keys[key]

    def load(self, config="default"):
        self.config = config
        path = os.path.dirname(os.path.abspath(__file__))

        def abs_path(filename):
            return os.path.join(path, "config", "{}.yaml".format(filename))

        with open(abs_path("default")) as c:
            self.keys = yaml.load(c)

        self.keys['credentials'] = {}
        if os.path.exists(abs_path("credentials")):
            with open(abs_path("credentials")) as c:
                self.keys['credentials'] = yaml.load(c) or {}

        if config != "default":
            with open(abs_path(config)) as c:
                self.keys.update(yaml.load(c))

config = Config()
