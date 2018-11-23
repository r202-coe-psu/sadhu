import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.md')) as f:
    CHANGES = f.read()

requires = []
with open('requirements.txt', 'r') as fp:
    requires = [t.strip() for t in fp.read().split('\n') \
                if len(t.strip()) > 0]

init = os.path.join(os.path.dirname(__file__), 'sadhu', '__init__.py')
version_line = list(filter(lambda l: l.startswith('__version__'), open(init)))[0]
VERSION = version_line.split('=')[-1].replace('\'', '').strip()

setup(name='sadhu',
      version=VERSION,
      description='',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="sadhu",
      entry_points="""\
      [console_scripts]
      sadhu-web = sadhu.cmd.web:main

      """,
      )
