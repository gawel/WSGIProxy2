# -*- coding: utf-8 -*-
from doctest import ELLIPSIS
from webtest.debugapp import debug_app
from webtest.http import StopableWSGIServer


def setup_test(test):
    test.globs['server'] = StopableWSGIServer.create(debug_app)
    test.globs['application_url'] = test.globs['server'].application_url
    for example in test.examples:
        example.options.setdefault(ELLIPSIS, 1)

setup_test.__test__ = False


def teardown_test(test):
    test.globs['server'].shutdown()
