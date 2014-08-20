import __builtin__
import itertools
import re

from rdc.dic.util import cached_property

CALL = object()
SETATTR = object()
module_regex = re.compile(r"\w+(\.\w+)*$").match


def dereference(x):
    # While x is a reference, resolve it.
    while callable(x) and hasattr(x, '__reference__') and x.__reference__:
        x = x()

    # If x is a list, dereference each items into a new list
    if type(x) is list:
        x = list(dereference(i) for i in x)
    # If x is a tuple, dereference each items into a new list
    elif type(x) is tuple:
        x = tuple(dereference(i) for i in x)

    # TODO: how to be more generic ?

    return x


class Definition(object):
    __reference__ = True

    def __init__(self, factory, *args, **kwargs):
        self._factory = factory
        self._args = list(args) if args else []
        self._kwargs = dict(kwargs) if kwargs else {}
        self._setup = []

    @cached_property
    def factory(self):
        if callable(self._factory):
            return self._factory

        # is factory in builtins?
        if hasattr(__builtin__, self._factory):
            factory = getattr(__builtin__, self._factory)
            if callable(factory):
                return factory

        try:
            _module, _attr = self._factory.split(':', 1)
        except ValueError as e:
            raise ValueError('The factory path {0} is invalid. Expected format: {1}.'.format(repr(self._factory), repr(
                'path.to.module:factory_name')))

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

        return factory

    @cached_property
    def factory_short_name(self):
        def shorten(module):
            if module.startswith('__'):
                return None
            return '.'.join(map(lambda i: i[0], module.split('.')))

        name, module = self.factory.__name__, self.factory.__module__
        try:
            module, name = name.split(':')
        except ValueError:
            pass
        return '.'.join(filter(None, (shorten(module), name, )))

    def call(self, attr, *args, **kwargs):
        self._setup.append((CALL, (attr, args, kwargs, ), ))

    def setattr(self, attr, value):
        self._setup.append((SETATTR, (attr, value, )))

    def __call__(self, *args, **kwargs):
        a = map(dereference, self._args + list(args))
        k = dict((_k, dereference(_v)) for _k, _v in itertools.chain(self._kwargs.iteritems(), kwargs.iteritems()))
        o = dereference(self.factory)(*a, **k)

        for _type, _args in self._setup:
            if _type == CALL:
                attr, args, kwargs = _args
                args = map(dereference, args)
                kwargs = dict((_k, dereference(_v)) for _k, _v in kwargs.iteritems())
                getattr(o, attr)(*args, **kwargs)
            else:
                raise NotImplementedError('not implemented')

        return o

    def __repr__(self):
        return '{0}({1})'.format(self.factory_short_name, _repr_args(self._args, self._kwargs))


def _repr_args(args, kwargs):
    return ', '.join(
        filter(None, [
            ', '.join(map(repr, args)),
            ', '.join(map(lambda i: '{0}={1}'.format(*i), kwargs.iteritems())),
        ])
    )

