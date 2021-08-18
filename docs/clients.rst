==============================
Available http client adapters
==============================

.. autoclass:: wsgiproxy.proxies.HttpClient

.. autoclass:: wsgiproxy.urllib3_client.HttpClient

.. autoclass:: wsgiproxy.requests_client.HttpClient

Use your own HTTP client::

  >>> def client(uri, method, body, headers):
  ...       headers = [('Content-Length', '0')]
  ...       location = None # the Location header if any
  ...       body_iter = ['']
  ...       return '200 Ok', location, headers, body_iter

  >>> proxy = HostProxy(application_url, client=client)
