# -*- coding: utf-8 -*-
#
# Author: Romain Dorgueil <romain@dorgueil.net>
# Copyright: © 2011-2013 SARL Romain Dorgueil Conseil
#
import functools
import itertools

from rdc.dic.definition import Definition
from rdc.dic.logging import LoggerAware
from rdc.dic.reference import reference, is_reference, tuple_reference
from rdc.dic.scope import Scope, CachedScope, ThreadScope


def join(*args):
    return '.'.join(filter(None, args))



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
            'thread': ThreadScope(),
            }

        if callable(self.configure):
            self.configure(self, *args, **kwargs)
        elif len(args) or len(kwargs):
            raise TypeError('Container of type {0} takes no arguments ({1} given)'.format(type(self), len(args) + len(kwargs)))

    def define(self, name, definition, scope=None, allow_override=False):
        scope = scope or 'container'
        self.logger.debug('[container#{id}] {cls}.define({name!r}, {definition!r}, {scope!r}, {allow_override!r})'.format(cls=type(self).__name__, id=id(self), **locals()))
        if name and not allow_override and name in self.refs:
            raise KeyError('Service container already have a definition for "{0}".'.format(name))

        scope_name, scope = scope, self.scopes[scope]

        ref = scope.define(name, definition)
        ref._scope = scope_name
        if name:
            self.refs[name] = ref

        return ref

    def definition(self, prefix, *args, **kwargs):
        self.logger.debug('[container#{id}] {cls}.definition({prefix!r}, *{args!r}, **{kwargs!r})'.format(cls=type(self).__name__, id=id(self), **locals()))
        def decorator(factory):
            return self.define('.'.join(filter(None, [prefix, factory.__name__])), Definition(factory, *args, **kwargs))
        return decorator

    def set_parameter(self, name, value, allow_override=False):
        self.logger.debug('[container#{id}] {cls}.set_parameter({name!r}, {value!r}, {allow_override!r})'.format(cls=type(self).__name__, id=id(self), **locals()))

        if not allow_override and name in self.refs:
            raise KeyError('Service container already have a definition for "{0}".'.format(name))

        self.parameters[name] = value
        self.refs[name] = reference(self.parameters.get, name)
        self.refs[name].repr = repr(value)
        return self.refs[name]

    def set_parameters(self, *args, **kwargs):
        namespace = kwargs.pop('namespace', None)
        return [
            self.set_parameter(join(namespace, k), v)
            for k, v in itertools.chain(
                *map(lambda i: i.iteritems(), args + (kwargs, ))
            )
        ]

    def get_parameter_names(self, *args, **kwargs):
        namespace = kwargs.pop('namespace', None)
        return [join(namespace, arg) for arg in args]

    def ref(self, name):
        if not name in self.refs:
            raise KeyError('Undefined service "{0}" requested.'.format(name))
        return self.refs[name]

    def get(self, name):
        return self.ref(name)()

    def scope_of(self, name):
        try:
            return self.ref(name)._scope
        except AttributeError as e:
            return None

    def set(self, key, value, lazy=False):
        self.logger.debug('[container#{id}] {cls}.set({key!r}, {value!r})'.format(cls=type(self).__name__, id=id(self), **locals()))
        if is_reference(value):
            return self.define(key, value)
        elif lazy:
            if isinstance(value, tuple):
                return self.define(key, tuple_reference(value))
            else:
                raise NotImplementedError('Lazy logic not implemented for {0}.'.format(type(value).__name__))
        return self.set_parameter(key, value)

    def inject(self, **inject_map):
        def inject_decorator(wrapped):
            @functools.wraps(wrapped)
            def _wrapped(*args, **kwargs):
                for k, v in inject_map.iteritems():
                    # todo : move at decorator level to raise at import instead of runtime
                    if k in kwargs:
                        raise KeyError('Duplicate parameter for {0}'.format(k))
                    if callable(v):
                        kwargs[k] = v(self)
                    else:
                        kwargs[k] = self.get(v)
                return wrapped(*args, **kwargs)
            return _wrapped
        return inject_decorator

    def __len__(self):
        return len(self.refs)

