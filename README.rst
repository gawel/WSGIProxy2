Installation
============

With pip::

  $ pip install wsgi_proxy

Install optionnal backends::

  $ pip install requests restkit urllib3


Usage
=====

Create a proxy::

  >>> from wsgi_proxy import HostProxy
  >>> proxy = HostProxy(application_url)

Then use it. Here is an example with WebOb but you can use it like a classic
WSGI application::

  >>> from webob import Request
  >>> req = Request.blank('/form.html')
  >>> resp = req.get_response(proxy)
  >>> print(resp.text)
  <html>...
  ...</html>

The Proxy application accept some keyword arguments. Those arguments are passed
to the client during the process.

Use `requests <http://pypi.python.org/pypi/requests>`_::

  >>> proxy = HostProxy(application_url, client='requests')

Use `restkit <http://pypi.python.org/pypi/restkit>`_::

  >>> proxy = HostProxy(application_url, client='restkit') # doctest: +SKIP

Use `urllib3 <http://pypi.python.org/pypi/urllib3>`_::

  >>> proxy = HostProxy(application_url, client='urllib3')

