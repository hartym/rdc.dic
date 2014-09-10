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
import threading

from abc import abstractmethod, ABCMeta

from rdc.dic.error import AbstractError
from rdc.dic.reference import reference


MODULE = re.compile(r"\w+(\.\w+)*$").match


class IScope:
    """
    Interface for dependency injection scopes.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def get(self, name):
        """Get an instance by service name. Whether or not a new instance should be created is left as an implementation
        choice, and different scopes may have different behavior about this."""
        raise AbstractError(self.get)

    @abstractmethod
    def build(self, name):
        """Builds an instance for service named `name`. This should not be called by user, as `get()` will call
        `build()` if the current scope implementation instance requires the creation of a new instance."""
        raise AbstractError(self.build)

    @abstractmethod
    def ref(self, name):
        """Returns a "reference" to a named `get()` call."""
        raise AbstractError(self.ref)

    @abstractmethod
    def definitions(self):
        """Iterator on definitions."""
        raise AbstractError(self.ref)

    @abstractmethod
    def services(self):
        """Iterator on services."""
        raise AbstractError(self.ref)


class Scope(IScope, object):
    """
    Dependency injection scope that returns a new instance for a given service each time get(service_name) is called.
    """

    def __init__(self, container=None):
        self.container = container
        self._definitions = {}

    def define(self, name, definition):
        """Create definition and return a callable getter."""
        self._definitions[name] = definition
        return self.ref(name, repr=definition)

    def build(self, name):
        """Create an instance."""
        return self._definitions[name]()

    get = build

    def ref(self, name, repr=None):
        ref = reference(self.get, name)
        if repr is not None:
            ref.repr = repr
        return ref

    def definitions(self):
        for name, definition in sorted(self._definitions.iteritems()):
            yield name, definition

    def services(self):
        """No service instance for prototype level scope"""
        if 0:
            yield


class CachedScope(Scope):
    """
    Dependency injection scope that returns the same instance for a given service each time get(service_name) is called.
    """

    def __init__(self, container=None):
        super(CachedScope, self).__init__(container)
        self._services = {}

    def get(self, name):
        """Get in scope or build."""
        if not name in self._services:
            self._services[name] = self.build(name)
        return self._services[name]

    def services(self):
        for id, service in sorted(self._services.iteritems()):
            yield id, service


class NamespacedScope(CachedScope):
    """
    A thread that store service instances by "namespace", if provided.
    """

    def __init__(self, container=None):
        super(NamespacedScope, self).__init__(container)
        self._current_namespace = None

    @property
    def current_namespace(self):
        return str(self._current_namespace)

    @current_namespace.setter
    def current_namespace(self, value):
        self._current_namespace = value

    def get(self, name):
        ns = self.current_namespace
        if not ns in self._services:
            self._services[ns] = {}
        if not name in self._services[ns]:
            self._services[ns][name] = self.build(name)
        return self._services[ns][name]

    def services(self):
        for ns, ns_services in sorted(self._services.iteritems()):
            for id, service in sorted(ns_services.iteritems()):
                yield (ns, id, ), service

    def enter(self, namespace):
        self._current_namespace = str(namespace)
        self._services[namespace] = {}

    def leave(self, namespace):
        del self._services[namespace]
        if namespace == self.current_namespace:
            self._current_namespace = None

class ThreadLocalScope(NamespacedScope):
    @property
    def current_namespace(self):
        return str(threading.current_thread().name)




