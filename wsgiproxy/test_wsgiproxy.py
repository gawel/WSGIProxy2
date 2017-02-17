# -*- coding: utf-8 -*-
import unittest
from wsgiproxy import proxies
from webtest import TestApp
from webtest.debugapp import debug_app
from webtest.http import StopableWSGIServer
from webob import Request
import logging
import socket

logging.getLogger('waitress').setLevel(logging.DEBUG)


def start_response(*args):
    pass


class TestHttplib(unittest.TestCase):

    client = 'httplib'
    client_options = {}

    def setUp(self):
        self.server = StopableWSGIServer.create(debug_app)
        self.application_url = self.server.application_url.rstrip('/')
        self.proxy = proxies.HostProxy(self.application_url,
                                       client=self.client,
                                       **self.client_options)
        self.app = TestApp(self.proxy)

    def test_form(self):
        resp = self.app.get('/form.html')
        resp.mustcontain('</form>')
        form = resp.form
        form['name'] = 'gawel'
        resp = form.submit()
        resp.mustcontain('name=gawel')

    def test_head(self):
        resp = self.app.head('/form.html')
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(len(resp.body), 0)

    def test_webob_error(self):
        req = Request.blank('/')
        req.content_length = '-1'
        resp = req.get_response(self.proxy)
        self.assertEqual(resp.status_int, 500, resp)

    def test_status(self):
        resp = self.app.get('/?status=404', status='*')
        self.assertEqual(resp.status_int, 404)

    def test_redirect(self):
        location = self.application_url + '/form.html'
        resp = self.app.get(
            '/?status=301%20Redirect&header-location=' + location,
            status='*')
        self.assertEqual(resp.status_int, 301, resp)
        self.assertEqual(resp.location, location)

        location = 'http://foo.com'
        resp = self.app.get(
            '/?status=301%20Redirect&header-location=' + location,
            status='*')
        self.assertEqual(resp.status_int, 301, resp)
        self.assertEqual(resp.location, location)

        location = '/foo'
        resp = self.app.get(
            '/?status=301%20Redirect&header-location=' + location,
            status='*')
        self.assertEqual(resp.status_int, 301, resp)
        self.assertEqual(resp.location, self.application_url + location)

        location = self.application_url + '/script_name/form.html'
        self.proxy.strip_script_name = False
        resp = self.app.get(
            '/?status=301%20Redirect&header-Location=' + location,
            status='*', extra_environ={'SCRIPT_NAME': '/script_name'})
        self.assertEqual(resp.status_int, 301, resp)
        self.assertEqual(resp.location, location)

    def test_chunked(self):
        resp = self.app.get('/',
                            headers=[('Transfer-Encoding', 'chunked')])
        resp.mustcontain(no='chunked')

    def test_quoted_utf8_url(self):
        path = '/targets/NR2F1%C3%82-human/'
        resp = self.app.get(path)
        resp.mustcontain(b'PATH_INFO: /targets/NR2F1\xc3\x82-human/')

    def tearDown(self):
        self.server.shutdown()


class TestUrllib3(TestHttplib):

    client = 'urllib3'


class TestRequests(TestHttplib):

    client = 'requests'


class TestExtractUri(unittest.TestCase):

    def test_proxy(self):
        environ = Request.blank('/').environ.copy()
        proxy = proxies.Proxy()
        if 'SERVER_NAME' in environ:
            del environ['SERVER_NAME']
        uri = proxy.extract_uri(environ)
        self.assertEqual(uri, 'http://localhost:80')

        environ['SERVER_NAME'] = 'foo'
        environ['SERVER_PORT'] = '8080'
        uri = proxy.extract_uri(environ)
        self.assertEqual(uri, 'http://foo:8080')

        del environ['SERVER_PORT']
        del environ['HTTP_HOST']
        environ['SERVER_NAME'] = 'foo'
        environ['wsgi.url_scheme'] = 'https'
        uri = proxy.extract_uri(environ)
        self.assertEqual(uri, 'https://foo:443')

    def test_transparent_proxy(self):
        req = Request.blank('/')
        proxy = proxies.TransparentProxy()
        uri = proxy.extract_uri(req.environ)
        self.assertEqual(uri, 'http://localhost:80')

        req.scheme = 'https'
        req.environ['HTTP_HOST'] = 'foo'
        uri = proxy.extract_uri(req.environ)
        self.assertEqual(uri, 'https://foo:443')


class TestMisc(unittest.TestCase):

    def test_socket_gaierror(self):
        def client(*args):
            raise socket.gaierror()
        proxy = proxies.Proxy(client)
        app = TestApp(proxy)
        resp = app.get('/', status='*')
        self.assertEqual(resp.status_int, 502)

    def test_socket_timeout(self):
        def client(*args):
            raise socket.timeout()
        proxy = proxies.Proxy(client)
        app = TestApp(proxy)
        resp = app.get('/', status='*')
        self.assertEqual(resp.status_int, 504)

    def test_exception(self):
        def client(*args):
            raise ValueError()
        proxy = proxies.Proxy(client)
        app = TestApp(proxy)
        resp = app.get('/', status='*')
        self.assertEqual(resp.status_int, 500)

    def test_rewrite_location(self):
        location = proxies.rewrite_location('http://localhost:80', '/foo')
        self.assertEqual(location, 'http://localhost:80/foo')

        location = proxies.rewrite_location('http://localhost:80',
                                            '/foo', '/path')
        self.assertEqual(location, 'http://localhost:80/path/foo')

        location = proxies.rewrite_location('http://localhost:80',
                                            'http://localhost:80/foo', '/path')
        self.assertEqual(location, 'http://localhost:80/path/foo')


class DummyConnection(object):

    def __init__(self, *args, **kwargs):
        pass

    def request(self, *args, **kwargs):
        raise kwargs['exc']
