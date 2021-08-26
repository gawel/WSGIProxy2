from setuptools import setup, find_packages

version = '0.5.1'


def read(name):
    try:
        with open(name) as fd:
            return fd.read()
    except Exception:
        return ''


setup(name='WSGIProxy2',
      version=version,
      long_description=read('README.rst') + '\n' + read('CHANGES.rst'),
      description='A WSGI Proxy with various http client backends',
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
      ],
      keywords='wsgi proxy',
      author='Gael Pasgrimaud',
      author_email='gael@gawel.org',
      url='https://github.com/gawel/WSGIProxy2/',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'README_fixt', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=['webob'],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
