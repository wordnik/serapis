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

import requests
import pattern
from dateutil.parser import parse as parse_date
from .config import config  # Make sure to use absolute imports here
from serapis.language import is_english
from serapis.extract import PageRequest
import pattern.web
from serapis.util import async
import time
import logging
log = logging.getLogger('serapis')

GOOGLE = pattern.web.Google(license=config.credentials.get('google'), language='en')


def search(term):
    """
    Performs an asynchronous search operation on various services.

    Args:
        term: str -- term to search for
    Returns:
        list -- List of url objects containing url, doc, author, and other keys.
    """
    log.info("Sarching for '{}'".format(term))
    ddg = async(search_duckduckgo, term)
    search = async(search_and_parse, search_google, term)

    while not (ddg.done and search.done):
        time.sleep(.5)
    combined = (ddg.value or []) + (search.value or [])
    result = [url_object for url_object in combined if url_object and url_object.get('doc')]
    log.info("Parsing URLs for '{}' yielded {} results".format(term, len(result)))
    return result


def search_and_parse(search_func, term):
    """
    Wrapper for asynchronous search and parsing. Performs a search and calls
    diffbot's API for each result in parallel. Returns after all results are
    parsed by diffbot.

    Args:
        search_func: function -- Search function, e.g. search_google
        term: str -- Term to search for
    Returns:
         list -- List of url objects containing url, doc, author, and other keys.
    """
    search_result = search_func(term)
    # diffbot_parse_batch(result)  # @TODO
    jobs = [async(extract_wrapper, url_object, term) for url_object in search_result]
    while not all(job.done for job in jobs):
        time.sleep(.5)
    result = [job.value for job in jobs if job.value]
    log.info("Parsing URLs for '{}' yielded {} results".format(term, len(result)))
    return result


def extract_wrapper(url_object, term):
    return PageRequest(url_object['url']).get_structured_page()


def diffbot_parse(url_object):
    """
    Returns the article text for a single URL.

    Args:
        url_object: dict -- Containing at least a 'url' item
    Returns:
        dict -- the url_object, extended with text, author, and features
    """
    log.info("Using diffbot to parse {}".format(url_object['url']))
    response = requests.get("http://api.diffbot.com/v3/article", params={
        "token": config.credentials['diffbot'],
        "url": url_object['url'],
        "discussion": False
    })
    json = response.json()
    # assert json.get('objects')
    result = json['objects'][0]
    url_object['doc'] = result.get('text', "")
    url_object['author'] = result.get('author')
    url_object['source'] = result.get('siteName')
    url_object['features'] = html_to_features(result.get('html'), "")
    return url_object


def html_to_features(html, term):
    """
    Detects features present in a html document.

    Args:
        html: str -- String containing HTML code
        term: str -- Term to search for
    Returns:
        dict -- Feature flags
    """
    # @TODO
    return {}


def search_diffbot_cache(word):
    response = requests.get('http://api.diffbot.com/v3/search', params={
        'token': config.credentials['diffbot'],
        'query': requests.utils.quote('"{}"'.format(word)),
        'col': 'GLOBAL-INDEX'
    }).json()
    if not response.get('objects'):
        if response.get('error'):
            print("Response Error '{}' (code: {})".format(response['error'], response['errorCode']))
        else:
            print("NO RESULTS")
    results = []
    for object in response.get('objects', []):
        if object.get('text'):
            result = {
                "title": object.get('title'),
                "url": object.get('pageUrl'),
                "author": object.get('author'),
                "date": parse_date(object.get('date', '')).isoformat(),
                "doc": object.get('text')
            }
            results.append(result)
    return results


def search_duckduckgo(term):
    result = []
    try:
        req = requests.get('http://api.duckduckgo.com/?q={}&format=json'.format(term)).json()
    except:
        return result
    if req['AbstractSource'] not in config.duckduckgo_sources:
        return result
    if req.get('Abstract'):
        result.append({
            'title': req['Heading'],
            'url': req['AbstractURL'],
            'author': None,
            'date': None,
            'source': req['AbstractSource'],
            'doc': req['Abstract']
        })
    if req.get('Definition'):
        result.append({
            'title': req['Heading'],
            'url': req['DefinitionURL'],
            'source': req['DefinitionSource'],
            'author': None,
            'date': None,
            'doc': req['Definition']
        })
    log.info("Searching DuckDuckGo for '{}' returned {} results".format(term, len(result)))
    return result


def search_google(term):
    result = []
    response = GOOGLE.search(term, type=pattern.web.SEARCH)
    for url_object in response:
        if is_english(url_object['text']) and \
           'wikipedia.org' not in url_object['url']:  # We get this from DuckDuckGo
            result.append({
                'url': url_object['url'],
                'date': parse_date(url_object.get('date')).isoformat(),
                'title': url_object['title']
            })
    log.info("Searching Google for '{}' returned {} results".format(term, len(result)))
    return result
