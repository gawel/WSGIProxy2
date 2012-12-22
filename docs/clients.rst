==============================
Available http client adapters
==============================

.. autoclass:: wsgi_proxy.proxies.HttpClient

.. autoclass:: wsgi_proxy.urllib3_client.HttpClient

.. autoclass:: wsgi_proxy.requests_client.HttpClient

.. autoclass:: wsgi_proxy.restkit_client.HttpClient

Use your own HTTP client::

  >>> def client(uri, method, body, headers):
  ...       headers = [('Content-Length', '0')]
  ...       location = None # the Location header if any
  ...       body_iter = ['']
  ...       return '200 Ok', location, headers, body_iter

  >>> proxy = HostProxy(application_url, client=client)
