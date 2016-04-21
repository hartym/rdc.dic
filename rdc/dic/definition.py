# -*- coding: utf-8 -*-
#
# Copyright 2012-2016 Romain Dorgueil
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import builtins
import itertools
import re

from rdc.dic.util import cached_property
import collections

CALL = object()
SETATTR = object()
module_regex = re.compile(r"\w+(\.\w+)*$").match


def dereference(x):
    # While x is a reference, resolve it.
    while isinstance(x, collections.Callable) and hasattr(x, '__reference__') and x.__reference__:
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
        self._name = None
        self._module = None
        self._args = list(args) if args else []
        self._kwargs = dict(kwargs) if kwargs else {}
        self._setup = []

    @cached_property
    def factory(self):
        if isinstance(self._factory, collections.Callable):
            return self._factory

        # is factory in builtins?
        if hasattr(builtins, self._factory):
            factory = getattr(builtins, self._factory)
            if isinstance(factory, collections.Callable):
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
                print('Could not import {0}'.format(_module))
                raise

            try:
                entry = getattr(entry, _attr)
            except AttributeError:
                print('{0} has no {1} attribute.'.format(entry, _attr))
                raise

            return entry(*args, **kwargs)

        factory.__name__ = str(_attr)
        factory.__module__ = str(_module)

        return factory

    @cached_property
    def __name__(self):
        if not self._name:
            self._name = self.factory.__name__
        return self._name

    @cached_property
    def __module__(self):
        if not self._module:
            self._module = self.factory.__module__
        return self._module

    @cached_property
    def factory_short_name(self):
        def shorten(module):
            if module.startswith('__'):
                return None
            return '.'.join([i[0] for i in module.split('.')])

        return '.'.join([_f for _f in (shorten(self.__module__), self.__name__,) if _f])

    def call(self, attr, *args, **kwargs):
        self._setup.append((CALL, (attr, args, kwargs,),))

    def setattr(self, attr, value):
        self._setup.append((SETATTR, (attr, value,)))

    def __call__(self, *args, **kwargs):
        a = list(map(dereference, self._args + list(args)))
        k = dict((_k, dereference(_v)) for _k, _v in itertools.chain(iter(self._kwargs.items()), iter(kwargs.items())))
        o = dereference(self.factory)(*a, **k)

        for _type, _args in self._setup:
            if _type == CALL:
                attr, args, kwargs = _args
                args = list(map(dereference, args))
                kwargs = dict((_k, dereference(_v)) for _k, _v in kwargs.items())
                getattr(o, attr)(*args, **kwargs)
            else:
                raise NotImplementedError('not implemented')

        return o

    def __repr__(self):
        return '{0}({1})'.format(self.factory_short_name, _repr_args(self._args, self._kwargs))


def _repr_args(args, kwargs):
    return ', '.join(
        [_f for _f in [
            ', '.join(map(repr, args)),
            ', '.join(['{0}={1}'.format(*i) for i in iter(kwargs.items())]),
        ] if _f]
    )
