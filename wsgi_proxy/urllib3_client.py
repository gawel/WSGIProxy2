# -*- coding: utf-8 -*-
import urllib3


class HttpClient(object):
    """A HTTP client using urllib3"""

    default_options = dict(redirect=False)

    def __init__(self, pool=None, **urlopen_options):
        self.pool = pool or urllib3.PoolManager(10)
        options = self.default_options.copy()
        options.update(urlopen_options)
        self.options = options

    def __call__(self, uri, method, body, headers):
        if 'Transfer-Encoding' in headers:
            del headers['Transfer-Encoding']
        if headers.get('Content-Length'):
            body = body.read(int(headers['Content-Length']))
        elif body is not None:
            body = body.read()
        kwargs = self.options.copy()
        kwargs.update(body=body, headers=headers)
        response = self.pool.urlopen(method, uri, **kwargs)
        status = '%s %s' % (response.status, response.reason)
        headers = [(k.title(), v) for k, v in response.getheaders().items()]
        return (status, response.getheader('location', None),
                headers, [response.data])
