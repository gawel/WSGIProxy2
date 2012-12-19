from setuptools import setup, find_packages

version = '0.1'

setup(name='wsgi_proxy',
      version=version,
      description="",
      long_description="""\
""",
      classifiers=[],
      keywords='',
      author='Gael Pasgrimaud',
      author_email='gael@gawel.org',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=['webob', 'six'],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
