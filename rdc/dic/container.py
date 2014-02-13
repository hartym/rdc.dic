# -*- coding: utf-8 -*-
#
# Author: Romain Dorgueil <romain@dorgueil.net>
# Copyright: © 2011-2013 SARL Romain Dorgueil Conseil
#
from rdc.dic.definition import Definition
from rdc.dic.reference import reference
from rdc.dic.scope import Scope, CachedScope

class Container(object):
    def __init__(self, *args, **kwargs):
        self.refs = {
            'container': reference(self)
        }
        self.parameters = {}
        self.scopes = {
            'prototype': Scope(),
            'container': CachedScope(),
            }

        self.configure(self, *args, **kwargs)

    @staticmethod
    def configure(self, *args, **kwargs):
        pass

    def load_module(self, name, *args, **kwargs):
        __import__(name, fromlist=['Container']).Container.configure(self, *args, **kwargs)

    def define(self, name, definition, scope='container', allow_override=False):
        if name and not allow_override and name in self.refs:
            raise KeyError('Service container already have a definition for "{0}".'.format(name))

        scope_name, scope = scope, self.scopes[scope]

        ref = scope.define(name, definition)
        ref._scope = scope_name
        if name:
            self.refs[name] = ref

        return ref

    def definition(self, prefix, *args, **kwargs):
        def decorator(factory):
            return self.define('.'.join(filter(None, [prefix, factory.__name__])), Definition(factory, *args, **kwargs))
        return decorator

    def set_parameter(self, name, value, allow_override=False):
        if not allow_override and name in self.refs:
            raise KeyError('Service container already have a definition for "{0}".'.format(name))

        self.parameters[name] = value
        self.refs[name] = reference(self.parameters.get, name)
        self.refs[name].repr = repr(value)
        return self.refs[name]

    def set_parameters(self, parameters):
        return [self.set_parameter(name, value) for name, value in parameters.iteritems()]

    def get_parameters(self, *args, **kwargs):
        namespace = kwargs.pop('namespace', None)
        return ['.'.join(filter(None, [namespace, arg])) for arg in args]

    def ref(self, name):
        return self.refs[name]

    def get(self, name):
        return self.ref(name)()

