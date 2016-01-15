#!/usr/bin/env python2
# coding=utf-8
"""
Utility belt
"""
from __future__ import unicode_literals
from __future__ import absolute_import
from functools import wraps

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-09"
__email__ = "manuel@summer.ai"

import hashlib
import re
from unidecode import unidecode
import threading
import traceback
import functools32 as functools
import logging
import unicodecsv as csv
import datetime
from urlparse import urlparse

log = logging.getLogger('serapis.search')


class AsynchronousRequest(object):
    """Class for threaded function calls. Usage:

    >>> urls = ("http://summer.ai", "http://google.com")
    >>> jobs = [AsynchronousRequest(crawl, url) for url in urls]
    >>> while not all(jobs):
    >>>     time.sleep(.5)
    >>> results = [job.value for job in jobs]

    Note that AsynchronousRequest will be falsey until the function
    returns or raises an exception. You can explicitly check whether
    the request is completed with AsynchronousRequest.done

    Properties:
        value -- return value of the function (or None)
        error -- Exception raised, if any
        done -- True if the function has returned or raised an Exception
    """
    def __init__(self, function, *args, **kwargs):
        """
        Args:
            function: func -- function to call asynchronously
            args, kwargs -- arguments to the function
        Returns:
            AsynchronousRequest
        """
        self.value = None
        self.error = None
        self._function = function
        self._thread = threading.Thread(target=self._fetch, args=(function,) + args, kwargs=kwargs)
        self._thread.start()

    def _fetch(self, function, *args, **kwargs):
        try:
            self.value = function(*args, **kwargs)
        except Exception as e:
            log.error("Exception in AsynchronousRequest '{}' -- {}".format(function.__name__, traceback.format_exc()))
            self.error = e

    @property
    def done(self):
        return not self._thread.isAlive()

    def __nonzero__(self):
        return self.done


def now():
    """Returns the current date and time in ISO8601 format.

    Returns:
        str -- e.g. '2015-12-17T20:21:10'
    """
    return datetime.datetime.now().replace(microsecond=0,).isoformat()


def merge_dict(target, *to_merge):
    """Merges dictionaries into a target. If keys already exist,
    only merges target if they are not falsey.

    Args:
        target: dict -- Will be modified
        *to_merge: dicts -- Will be merged into target
    Returns:
        dict -- modified target
    """
    for d in to_merge:
        if d:
            for k, v in d.items():
                if k not in target or d[k]:
                    target[k] = d[k]
    return target


@functools.lru_cache()
def squashed(text, keep=''):
    """Turns "I've had a Déjà Vu!" into 'ivehadadejavu'. It
    will try to normalize all characters to ASCII and remove
    anything that's not a letter or number.

    >>> squashed('deja-vu') in squashed('I had a Déjà Vu')
    >>> True

    Results are cached.

    Args:
        text: str
        keep: str -- Characters to keep, e.g. HTML tags.
    Returns:
        str
    """
    return re.sub(r"[^a-z0-9{}]".format(keep), "", unidecode(text).lower())


def multiple_replace(text, replacements, re_style=False):
    """Makes several replacements in a string.

    Args:
        text: str
        replacements: dict -- Maps parts to be replaced to substitutions
        re_style: bool -- If True, wrap replacements in group brackets
    Returns:
        str
    """
    rx = re.compile('|'.join(map(re.escape, replacements)))
    patch = "({})" if re_style else "{}"
    
    def one_xlat(match):
        return patch.format(replacements[match.group(0)])
    return rx.sub(one_xlat, text)


class Collector(object):
    """Collector decorator"""
    all = []

    def __init__(self, func):
        self.func = func
        self.all.append(func)
        wraps(func)(self)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


def singleton(cls):
    """Singleton decorator"""
    instances = {}

    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getinstance


def slugify(string):
    """
    Slugify a unicode string.

        >>> slugify(u"Héllø Wörld")
        u"hello-world"
    """
    return re.sub(r'[-\s]+', '-',
                  re.sub(r'[^\w\s-]', '', unidecode(string))
                  ).strip().lower()


def hashslug(word):
    """returns a slug and a short hash for a word, separated by a colon. EG

        >>> hashslug("L'esprit de l'escalier")
        'lesprit-de-lescalier:6ad283'

    """
    if not isinstance(word, unicode):
        word = word.decode('utf-8')
    return "{}:{}".format(
        slugify(word),
        hashlib.md5(word.encode('utf-8')).hexdigest()[:6]
    )


def read_csv(filename, skip_header=False):
    """Reads a CSV file and converts it into Unicode.

    Args:
        filename: str
        skip_header: bool -- If true, ignores the first row.
    """
    with open(filename, 'rb') as f:
        reader = csv.reader(f)
        rows = list(reader)
        return rows[1:] if skip_header else rows


def write_csv(rows, filename, header=None):
    """Writes a CSV file, encoding all text into UTF-8.

    Args:
        rows: iterable -- list of tuples or lists
        filename: str -- output filename
        header: tuple -- optional header row
    """
    with open(filename, 'wb') as f:
        writer = csv.writer(f)
        if header:
                writer.writerow(header)
        writer.writerows(rows)


def numeric_hash(string, digest_size=4):
    """
    Returns an integer hash of a string.

    Args:
        string: str -- String to hash
        digest_size: int -- Size of the digest in bytes. Max is 16.
    Returns:
        int
    """
    return int(hashlib.md5(string.encode("utf-8")).hexdigest()[:2 * digest_size], 16)


def get_source_from_url(url):
    """
    Extracts the Domain name without TLD from a url.

    >>> get_source_from_url('http://mashable.com/2013/10/30/new-media-technology/')
    >>> Mashable

    Args:
        url: str
    Returns:
        str
    """
    hostname = urlparse(url).hostname
    try:
        return hostname.replace(".co.", ".co").split(".")[-2].capitalize()
    except:
        return hostname


def batch(generator, batch_size=5):
    """Wraps around a generator and yields results in batches.

    Example:

        gen = (letter for letter in string.ascii_uppercase)
        for n in batch(gen, 8):
            print(''.join(n))

    Will produce:

        ABCDEFGH
        IJKLMNOP
        QRSTUVWX
        YZ
    """
    cont = True
    while cont:
        result = []
        for n in range(batch_size):
            try:
                result.append(next(generator))
            except StopIteration:
                cont = False
                break
        yield result
