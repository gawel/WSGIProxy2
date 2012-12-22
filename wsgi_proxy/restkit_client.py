# -*- coding: utf-8 -*-
from restkit.client import Client


class HttpClient(object):
    """A HTTP client using restkit"""

    def __init__(self, restkit_client=None, **restkit_options):
        self.client = restkit_client or Client(**restkit_options)

    def __call__(self, uri, method, body, headers):
        response = self.client.request(uri, method, body=body, headers=headers)
        location = response.headers.get('location') or None
        return (response.status, location,
                response.headerslist, response.tee())
