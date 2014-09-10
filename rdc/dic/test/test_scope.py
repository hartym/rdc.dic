# -*- coding: utf-8 -*-

from rdc.dic.scope import CachedScope, Scope, ThreadLocalScope
from rdc.dic.test import TestCase
from rdc.dic.definition import Definition

class OhMyObj(object):
    pass

from threading import Thread, current_thread

class MyThread(Thread):
    def __init__(self, scope):
        super(MyThread, self).__init__()

        self.scope = scope
        self.result = None

    def run(self):
        print(self.name)
        print(current_thread())
        print(current_thread().ident)
        self.result = self.scope.get('foo')

class ScopeTestCase(TestCase):
    def build(self, ScopeType):
        scope = ScopeType()
        scope.define('foo', Definition(OhMyObj))
        scope.define('bar', Definition(OhMyObj))

        return scope

    def test_scope(self):
        scope = self.build(ScopeType=Scope)

        # A "normal" scope will return different instances for two calls targeting the same service
        self.assertIsNot(scope.get('foo'), scope.get('foo'))

    def test_cached_scope(self):
        scope = self.build(ScopeType=CachedScope)

        # A cached scope will return the same instance for two calls targeting the same service
        self.assertIs(scope.get('foo'), scope.get('foo'))

        # ... but different instances if there is two definitions using the same factory
        self.assertIsNot(scope.get('bar'), scope.get('foo'))

    def test_thread_scope(self):
        scope = self.build(ScopeType=ThreadLocalScope)

        self.assertIs(scope.get('foo'), scope.get('foo'))
        self.assertIsNot(scope.get('foo'), scope.get('bar'))

        t1 = MyThread(scope)
        t2 = MyThread(scope)

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        self.logger.info(scope.services)
        self.assertIsNot(t1.result, t2.result)


