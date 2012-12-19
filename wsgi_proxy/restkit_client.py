# -*- coding: utf-8 -*-
from restkit.client import Client


class HttpClient(object):

    def __init__(self, client=None, **kwargs):
        self.client = client or Client(**kwargs)

    def __call__(self, uri, method, body, headers):
        response = self.client.request(uri, method, body=body, headers=headers)
        location = response.headers.get('location') or None
        return (response.status, location,
                response.headerslist, response.tee())
