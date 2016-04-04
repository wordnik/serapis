#!/usr/bin/env python2
# coding=utf-8
"""
AWS Elastic Search connector
"""
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import print_function

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2016, summer.ai"
__date__ = "2016-02-15"
__email__ = "manuel@summer.ai"


from boto.connection import AWSAuthConnection
from elasticsearch import Connection
from urlparse import urlparse
from serapis.config import config
import time
import os


class ESConnection(AWSAuthConnection):
    """AWS AUth Connection for ElasticSearch"""

    def __init__(self, region, **kwargs):
        super(ESConnection, self).__init__(**kwargs)
        self._set_auth_region_name(region)
        self._set_auth_service_name("es")

    def _required_auth_capability(self):
        return ['hmac-v4']


class AWSConnection(Connection):
    """AWS Connection for ElasticSearch, able to perform signed requests."""

    def __init__(self, host, region, **kwargs):
        super(AWSConnection, self).__init__(host, region, **kwargs)
        self.host = host
        self.region = region
        self.token = kwargs.get('session_token')  # or os.environ.get('AWS_SESSION_TOKEN')
        self.key = kwargs.get('access_key') or config.credentials.aws_access_key
        self.secret = kwargs.get('secret_key') or config.credentials.aws_access_secret
        self.kwargs = kwargs

    def perform_request(self, method, url, params=None, body=None, timeout=None, ignore=()):
        """Makes a signed requests to ElasticSearch."""
        start = time.time()
        host = urlparse(self.host).netloc.split(':')[0]
        client = ESConnection(region=self.region,
                              host=self.host,
                              aws_access_key_id=self.key,
                              aws_secret_access_key=self.secret,
                              security_token=self.token,
                              is_secure=False)
        if isinstance(method, unicode):
            method = method.encode('utf-8')
        if isinstance(url, unicode):
            url = url.encode('utf-8')
        if body:
            response = client.make_request(method, path=url, params=params, data=body)
        else:
            response = client.make_request(method, path=url, params=params)

        duration = time.time() - start
        raw_data = response.read().decode('utf-8')

        if not (200 <= response.status < 300) and response.status not in ignore:
            self.log_request_fail(method, host, body, duration, response.status)
            self._raise_error(response.status, raw_data)

        return response.status, dict(response.getheaders()), raw_data
