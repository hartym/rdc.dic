# -*- coding: utf-8 -*-
#
# Copyright 2012-2014 Romain Dorgueil
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

import re
from rdc.dic.reference import Reference

MODULE = re.compile(r"\w+(\.\w+)*$").match

class Scope(object):
    """
    Service scope that returns  a new instance for a given service each time get(service_name) is called.
    """

    def __init__(self, container=None):
        self.container = container
        self.definitions = {}

    def define(self, name, factory, args=None, kwargs=None, calls=None):
        """Create definition and return a callable getter."""
        src = factory

        # simple "lazy import" implementation, borrowed from pkg_resources.EntryPoint.parse(...)
        if not callable(factory):
            _module, _attr = src.split(':', 1)
            if not MODULE(_module):
                raise ValueError('Invalid module name {0}'.format(_module))
            def factory(*args, **kwargs):
                entry = __import__(_module, globals(), globals(), ['__name__'])
                try:
                    entry = getattr(entry, _attr)
                except AttributeError:
                    raise ImportError('{0} has no {1} attribute.'.format(entry, attr))
                return entry(*args, **kwargs)
            factory.__name__ = src

        self.definitions[name] = (factory, args, kwargs, calls, )
        return self.ref(name, repr=src)

    def build(self, name):
        """Create an instance."""
        # get definition
        factory, args, kwargs, calls = self.definitions[name]
        # defaults and dereferencing
        args, kwargs = map(Reference.dereference, args or ()), dict((_k, Reference.dereference(_v)) for _k, _v in (kwargs or {}).iteritems())
        # build
        return Reference.dereference(factory)(*args, **kwargs)

    def ref(self, name, repr=None):
        ref = Reference(self.build, name)
        if repr is not None:
            ref._repr = repr
        return ref


class CachedScope(Scope):
    """
    Service scope that returns the same instance for a given service each time get(service_name) is called.
    """

    def __init__(self, container=None):
        super(CachedScope, self).__init__(container)
        self.services = {}

    def get(self, name):
        """Get in scope or build."""
        if not name in self.services:
            self.services[name] = self.build(name)
        return self.services[name]
