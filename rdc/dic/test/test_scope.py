# -*- coding: utf-8 -*-

from rdc.dic.scope import CachedScope, Scope
from rdc.dic.test import TestCase
from rdc.dic.definition import Definition

class OhMyObj(object):
    pass

class ScopeTestCase(TestCase):
    def test_scope(self):
        scope = Scope()
        scope.define('foo', Definition(OhMyObj))

        # A "normal" scope will return different instances for two calls targeting the same service
        self.assertIsNot(scope.get('foo'), scope.get('foo'))

    def test_class(self):
        scope = CachedScope()
        scope.define('foo', Definition(OhMyObj))
        scope.define('bar', Definition(OhMyObj))

        # A cached scope will return the same instance for two calls targeting the same service
        self.assertIs(scope.get('foo'), scope.get('foo'))

        # ... but different instances if there is two definitions using the same factory
        self.assertIsNot(scope.get('bar'), scope.get('foo'))

