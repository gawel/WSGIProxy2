Changes
=======

0.5.1 (unreleased)
------------------

- remove stale dep on six

- use github actions as CI


0.5.0 (2021-08-18)
------------------

- Drop support for python3.6 and bellow

0.4.6 (2019-02-22)
------------------

- PATCH added into (default) list of allowed methods


0.4.5 (2018-09-19)
------------------

- Allow to use URIs with no path


0.4.4 (2017-06-02)
------------------

- Clean up connection before returning result. This removes some
  ResourceWarnings when testing


0.4.3 (2017-02-17)
------------------

- Add OPTIONS to defaults allowed methods

- Drop restkit support

- Drop py26 support


0.4.2 (2014-12-20)
------------------

- Undo webob's unquoting to handle paths with percent quoted utf8 characters
  [Laurence Rowe]


0.4.1 (2013-12-21)
------------------

- Include README_fixt.py in release


0.4 (2013-12-21)
----------------

- fix tests.

- change the way requests iter response


0.3 (2013-09-12)
----------------

Make allowed_methods check optional

0.2
---

Return the data not gzip decoded when using request

0.1
---

Initial release
