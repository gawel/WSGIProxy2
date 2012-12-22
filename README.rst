==========
wsgi_proxy
==========

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
to requests during the process.  By default ``allow_redirects`` and ``verify``
are set to ``False`` but you can change the behavior::

  >>> proxy = HostProxy(application_url, verify=True, allow_redirects=True,
  ...                   max_redirects=10)

