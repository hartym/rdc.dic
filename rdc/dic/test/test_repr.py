# -*- coding: utf-8 -*-

from rdc.dic.test import TestCase
from rdc.dic.definition import Definition

class OhMyObj(object):
    pass

class SimpleTypesTestCase(TestCase):
    def test_builtin(self):
        self.assertEqual(repr(Definition(int, 42)), 'int(42)')
        self.assertEqual(repr(Definition(bool, True)), 'bool(True)')
        self.assertEqual(repr(Definition(bool, False)), 'bool(False)')
        self.assertEqual(repr(Definition(float, 3.14159)), 'float(3.14159)')
        self.assertEqual(repr(Definition(str, r'foo')), "str('foo')")
        self.assertEqual(repr(Definition(str, r"f'o'o")), "str(\"f'o'o\")")
        self.assertEqual(repr(Definition(str, 'Ô')), "unicode('\\xc3\\x94')")

    def test_class(self):
        self.assertEqual(repr(Definition(OhMyObj)), 'r.d.t.t.OhMyObj()')
        self.assertEqual(repr(Definition(OhMyObj, Definition(int, 42), foo=Definition(int, 1984))), 'r.d.t.t.OhMyObj(int(42), foo=int(1984))')

