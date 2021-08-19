# -*- coding: utf-8 -
from webob import exc
from webob.compat import PY3, url_quote
import logging
import socket
import re

try:
    import urlparse
except ImportError:  # pragma: nocover
    import urllib.parse as urlparse  # NOQA

try:
    import httplib
except ImportError:  # pragma: nocover
    import http.client as httplib  # NOQA

LOW_CHAR_SAFE = ''.join(chr(n) for n in range(128))

ABSOLUTE_URL_RE = re.compile(r"^https?://", re.I)

ALLOWED_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH']

WEBOB_ERROR = (
    "Content-Length is set to -1. This usually mean that WebOb has "
    "already parsed the content body. You should set the Content-Length "
    "header to the correct value before forwarding your request to the "
    "proxy: ``req.content_length = str(len(req.body));`` "
    "req.get_response(proxy)")


def rewrite_location(host_uri, location, prefix_path=None):
    prefix_path = prefix_path or ''
    url = urlparse.urlparse(location)
    host_url = urlparse.urlparse(host_uri)

    if not ABSOLUTE_URL_RE.match(location):
        # remote server doesn't follow rfc2616
        location = urlparse.urljoin(host_uri, location.lstrip('/'))
        prefix_path = prefix_path.strip('/')
        if prefix_path:
            location = location.replace(host_uri,
                                        host_uri + '/' + prefix_path)
        return location
    elif url.scheme == host_url.scheme and url.netloc == host_url.netloc:
        return urlparse.urlunparse((host_url.scheme, host_url.netloc,
                                    prefix_path + url.path, url.params,
                                    url.query, url.fragment))
    return location


class HttpClient(object):
    """A HTTP client using stdlib's httplib (Default client)"""

    HTTPConnection = httplib.HTTPConnection
    HTTPSConnection = httplib.HTTPSConnection

    def __init__(self, **connection_options):
        self.options = connection_options

    def __call__(self, uri, method, body, headers):
        ssl = uri.startswith('https://')
        ConnClass = ssl and self.HTTPSConnection or self.HTTPConnection
        uri = ssl and uri[8:] or uri[7:]
        port = ssl and 443 or 80
        try:
            host, path = uri.split('/', 1)
        except ValueError:
            host = uri
            path = ''
        path = '/' + path
        if ':' in host:
            host, port = host.split(':')
        conn = ConnClass('%s:%s' % (host, port))
        if 'Transfer-Encoding' in headers:
            del headers['Transfer-Encoding']
        if headers.get('Content-Length'):
            body = body.read(int(headers['Content-Length']))
        else:
            body = None
        conn.request(method, path, body, headers, **self.options)
        response = conn.getresponse()
        status = '%s %s' % (response.status, response.reason)
        length = response.getheader('content-length')
        resp_headers = [
            (k, v) for (k, v) in response.getheaders()
            if k.lower() != 'transfer-encoding'
        ]
        body = response.read(int(length)) if length else response.read()
        result = (status, response.getheader('location', None),
                  resp_headers, [body])
        conn.close()
        return result


class Proxy(object):
    """A proxy which redirect the request to SERVER_NAME:SERVER_PORT
    and send HTTP_HOST header"""

    header_map = {
        'HTTP_HOST': 'X_FORWARDED_SERVER',
        'SCRIPT_NAME': 'X_FORWARDED_SCRIPT_NAME',
        'wsgi.url_scheme': 'X_FORWARDED_SCHEME',
        'REMOTE_ADDR': 'X_FORWARDED_FOR',
    }

    def __init__(self, client=None, allowed_methods=ALLOWED_METHODS,
                 strip_script_name=True, **client_options):
        self.allowed_methods = allowed_methods
        self.strip_script_name = strip_script_name
        if client is None or client == 'httplib':
            self.http = HttpClient(**client_options)
        elif hasattr(client, '__call__'):
            self.http = client
        else:
            mod = __import__('wsgiproxy.%s_client' % client,
                             globals(), locals(), [''])
            self.http = mod.HttpClient(**client_options)
        self.logger = logging.getLogger(__name__)

    def extract_uri(self, environ):
        port = None
        scheme = environ['wsgi.url_scheme']
        if 'SERVER_NAME' in environ:
            host = environ['SERVER_NAME']
        else:
            host = environ['HTTP_HOST']
        if ':' in host:
            host, port = host.split(':')

        if not port:
            if 'SERVER_PORT' in environ:
                port = environ['SERVER_PORT']
            else:
                port = scheme == 'https' and '443' or '80'

        uri = '%s://%s:%s' % (scheme, host, port)
        return uri

    def process_request(self, uri, method, headers, environ):
        return self.http(uri, method, environ['wsgi.input'], headers)

    def __call__(self, environ, start_response):
        method = environ['REQUEST_METHOD']
        if (self.allowed_methods is not None and
                method not in self.allowed_methods):
                return exc.HTTPMethodNotAllowed()(environ, start_response)

        if 'RAW_URI' in environ:
            path_info = environ['RAW_URI']
        elif 'REQUEST_URI' in environ:
            path_info = environ['REQUEST_URI']
        else:
            if self.strip_script_name:
                path_info = ''
            else:
                path_info = environ['SCRIPT_NAME']
            path_info += environ['PATH_INFO']

            if PY3:
                path_info = url_quote(path_info.encode('latin-1'),
                                      LOW_CHAR_SAFE)

            query_string = environ['QUERY_STRING']
            if query_string:
                path_info += '?' + query_string

        for key, dest in self.header_map.items():
            value = environ.get(key)
            if value:
                environ['HTTP_%s' % dest] = value

        host_uri = self.extract_uri(environ)
        uri = host_uri + path_info

        new_headers = {}
        for k, v in environ.items():
            if k.startswith('HTTP_'):
                k = k[5:].replace('_', '-').title()
                new_headers[k] = v

        content_type = environ.get("CONTENT_TYPE")
        if content_type and content_type is not None:
            new_headers['Content-Type'] = content_type

        content_length = environ.get('CONTENT_LENGTH')
        transfer_encoding = environ.get('Transfer-Encoding', '').lower()
        if not content_length and transfer_encoding != 'chunked':
            new_headers['Transfer-Encoding'] = 'chunked'
        elif content_length:
            new_headers['Content-Length'] = content_length

        if new_headers.get('Content-Length', '0') == '-1':
            resp = exc.HTTPInternalServerError(detail=WEBOB_ERROR)
            return resp(environ, start_response)

        try:
            response = self.process_request(uri, method, new_headers, environ)
        except socket.timeout:
            return exc.HTTPGatewayTimeout()(environ, start_response)
        except (socket.error, socket.gaierror):
            return exc.HTTPBadGateway()(environ, start_response)
        except Exception as e:
            self.logger.exception(e)
            return exc.HTTPInternalServerError()(environ, start_response)

        status, location, headerslist, app_iter = response

        if location:
            if self.strip_script_name:
                prefix_path = environ['SCRIPT_NAME']
            else:
                prefix_path = None

            new_location = rewrite_location(host_uri, location,
                                            prefix_path=prefix_path)

            headers = []
            for k, v in headerslist:
                if k.lower() == 'location':
                    v = new_location
                headers.append((k, v))
        else:
            headers = headerslist

        start_response(status, headers)

        if method == "HEAD":
            return [b'']

        return app_iter


class TransparentProxy(Proxy):
    """A proxy based on HTTP_HOST environ variable"""

    def extract_uri(self, environ):
        port = None
        scheme = environ['wsgi.url_scheme']
        host = environ['HTTP_HOST']
        if ':' in host:
            host, port = host.split(':')

        if not port:
            port = scheme == 'https' and '443' or '80'

        uri = '%s://%s:%s' % (scheme, host, port)
        return uri


class HostProxy(Proxy):
    """A proxy to redirect all request to a specific uri"""

    def __init__(self, uri, client=None, allowed_methods=ALLOWED_METHODS,
                 strip_script_name=True, **client_options):
        super(HostProxy, self).__init__(
            client=client, allowed_methods=allowed_methods,
            strip_script_name=strip_script_name, **client_options)
        self.uri = str(uri.rstrip('/'))
        self.scheme, self.net_loc = urlparse.urlparse(self.uri)[0:2]

    def extract_uri(self, environ):
        environ['HTTP_HOST'] = self.net_loc
        return self.uri
