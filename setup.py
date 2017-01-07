# This file is autogenerated by edgy.project code generator.
# All changes will be overwritten.

import os
from setuptools import setup, find_packages

root_dir = os.path.dirname(os.path.abspath(__file__))

tolines = lambda c: list(filter(None, map(lambda s: s.strip(), c.split('\n'))))

def read(filename, flt=None):
    with open(filename) as f:
        content = f.read().strip()
        return flt(content) if callable(flt) else content

# Py3 compatibility hacks, borrowed from IPython.
try:
    execfile
except NameError:
    def execfile(fname, globs, locs=None):
        locs = locs or globs
        exec(compile(open(fname).read(), fname, "exec"), globs, locs)

version_ns = {}
execfile(os.path.join(root_dir, 'rdc/dic/_version.py'), version_ns)
version = version_ns.get('__version__', 'dev')

setup(
    name = 'rdc.dic',
    description = 'Dependency Injection',
    license = 'Apache License, Version 2.0',
    install_requires = ['lxml >=3.7,<3.8'],
    namespace_packages = ['rdc'],
    version = version,
    long_description = read('README.rst'),
    classifiers = read('classifiers.txt', tolines),
    packages = find_packages(exclude=['ez_setup', 'example', 'test']),
    include_package_data = True,
    extras_require = {'dev': ['coverage >=4.2,<4.3',
         'mock >=2.0,<2.1',
         'nose >=1.3,<1.4',
         'pylint >=1.6,<1.7',
         'pytest >=3,<4',
         'pytest-cov >=2.4,<2.5',
         'sphinx',
         'sphinx_rtd_theme',
         'yapf']},
    url = 'http://rdc.li/',
    download_url = 'https://github.com/rdcli/rdc.dic/tarball/{version}'.format(version=version),
)
