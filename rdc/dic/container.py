# -*- coding: utf-8 -*-
#
# Author: Romain Dorgueil <romain@dorgueil.net>
# Copyright: © 2011-2013 SARL Romain Dorgueil Conseil
#

from rdc.dic.definition import Definition
from rdc.dic.logging import LoggerAware
from rdc.dic.reference import reference, is_reference
from rdc.dic.scope import Scope, CachedScope


class Container(LoggerAware):
    configure = None

    def __init__(self, *args, **kwargs):
        self.refs = {
            'container': reference(self)
        }
        self.parameters = {}
        self.scopes = {
            'prototype': Scope(),
            'container': CachedScope(),
            }

        if callable(self.configure):
            self.configure(self, *args, **kwargs)
        elif len(args) or len(kwargs):
            raise TypeError('Container of type {0} takes no arguments ({1} given)'.format(type(self), len(args) + len(kwargs)))

    def define(self, name, definition, scope='container', allow_override=False):
        self.logger.debug('define({name!r}, {definition!r}, {scope!r}, {allow_override!r})'.format(name=name, definition=definition, scope=scope, allow_override=allow_override))
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
        self.logger.debug('set_parameter({name!r}, {value!r}, {allow_override!r})'.format(name=name, value=value, allow_override=allow_override))

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
        if not name in self.refs:
            raise KeyError('Undefined service "{0}" requested.'.format(name))
        return self.refs[name]

    def get(self, name):
        return self.ref(name)()

    def set(self, id, value):
        if is_reference(value):
            return self.define(id, value)
        return self.set_parameter(id, value)

    def __len__(self):
        return len(self.refs)

