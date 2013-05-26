# -*- coding: utf-8 -*-
import requests


class HttpClient(object):
    """A HTTP client using requests"""

    default_options = dict(verify=False, allow_redirects=False)

    def __init__(self, chunk_size=1024 * 24, session=None, **requests_options):
        options = self.default_options.copy()
        options.update(requests_options)
        self.options = options
        self.chunk_size = chunk_size
        self.session = session

    def __call__(self, uri, method, body, headers):
        kwargs = self.options.copy()
        kwargs['headers'] = headers
        if 'Transfer-Encoding' in headers:
            del headers['Transfer-Encoding']
        if headers.get('Content-Length'):
            kwargs['data'] = body.read(int(headers['Content-Length']))

        if self.session is None:
            session = requests.sessions.Session()
        else:
            session = self.session
        response = session.request(method, uri, **kwargs)

        location = response.headers.get('location') or None
        status = '%s %s' % (response.status_code, response.reason)
        headers = [(k.title(), v) for k, v in response.headers.items()]
        return (status, location, headers,
                response.iter_content(chunk_size=self.chunk_size))
