from functools import partial
import itertools
import re
from webapp2 import cached_property

CALL = object()
SETATTR = object()
module_regex = re.compile(r"\w+(\.\w+)*$").match

def dereference( ref_or_val):
    while isinstance(ref_or_val, (partial, Definition, )):
        ref_or_val = ref_or_val()
    return ref_or_val

class Definition(object):
    def __init__(self, factory, *args, **kwargs):
        self._factory = factory
        self._args = list(args) if args else []
        self._kwargs = dict(kwargs) if kwargs else {}
        self._setup = []

    @cached_property
    def factory(self):
        if not callable(self._factory):
            try:
                _module, _attr = self._factory.split(':', 1)
            except ValueError as e:
                raise ValueError('The factory path {0} is invalid. Expected format: {1}.'.format(repr(self._factory), repr('path.to.module:factory_name')))

            if not module_regex(_module):
                raise ValueError('Invalid module name {0}'.format(_module))

            def factory(*args, **kwargs):
                try:
                    entry = __import__(_module, globals(), globals(), ['__name__'])
                except:
                    print 'Could not import {0}'.format(_module)
                    raise

                try:
                    entry = getattr(entry, _attr)
                except AttributeError:
                    print '{0} has no {1} attribute.'.format(entry, _attr)
                    raise
                return entry(*args, **kwargs)

            factory.__name__ = self._factory
            self._factory = factory
        return self._factory

    def call(self, attr, *args, **kwargs):
        self._setup.append((CALL, (attr, args, kwargs, ), ))

    def setattr(self, attr, value):
        self._setup.append((SETATTR, (attr, value, )))

    def __call__(self, *args, **kwargs):
        a = map(dereference, self._args + list(args))
        k = dict((_k, dereference(_v)) for _k, _v in itertools.chain(self._kwargs.iteritems(), kwargs.iteritems()))
        return dereference(self.factory)(*a, **k)

    def __repr__(self):
        return '<Definition factory="{0}" *{1} **{2}>'.format(self._factory, self._args, self._kwargs)
