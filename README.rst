Installation
============

With pip::

  $ pip install WSGIProxy2

Install optionnal backends::

  $ pip install requests urllib3


Usage
=====

Create a proxy::

  >>> from wsgiproxy import HostProxy
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

If no client as specified then python httplib is used. It's recommended to use
a more robust client able to manage a connection pool and stuff.

Use `urllib3 <http://pypi.python.org/pypi/urllib3>`_::

  >>> proxy = HostProxy(application_url, client='urllib3')

Use `requests <http://pypi.python.org/pypi/requests>`_. This client support response streaming::

  >>> proxy = HostProxy(application_url, client='requests')

