#!/usr/bin/env python2
# coding=utf-8
"""
INIT

Logging setup

"""

from __future__ import unicode_literals
from __future__ import absolute_import

__author__ = "Manuel Ebert & Clare Corthell"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-09"
__email__ = "manuel@summer.ai"

import logging

logger = logging.getLogger('serapis')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

fh = logging.FileHandler('serapis.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)
