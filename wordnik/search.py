#!/usr/bin/env python
# coding=utf-8
"""
Search module
"""
from __future__ import unicode_literals
from __future__ import absolute_import

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-20"
__email__ = "manuel@summer.ai"

from config import config
import requests
from dateutil.parser import parse as parse_date


def search_diffbot_cache(word):
    results = requests.get('http://api.diffbot.com/v3/search', params={
        'token': config.credentials['diffbot'],
        'query': requests.utils.quote('"{}"'.format(word)),
        'col': 'GLOBAL-INDEX'
    }).json()
    if not results['objects']:
        print("NO RESULTS")
    for object in results['objects']:
        if object.get('text'):
            result = {
                "title": object.get('title'),
                "url": object.get('pageUrl'),
                "author": object.get('author'),
                "date": parse_date(object.get('date', '')).isoformat(),
                "doc": object.get('text')
            }
            yield result
