
from copy import copy
from rdc.dic.definition import Definition, dereference
from rdc.dic.reference import is_reference
from rdc.dic.test import TestCase


class DefinitionTestCase(TestCase):
    def assertIsDefinition(self, o):
        self.assertIsReference(o)
        self.assertIsInstance(o, Definition)

    def assertIsReference(self, o):
        self.assertTrue(is_reference(o))

    def test_integer(self):
        d = Definition(int, 42)
        self.assertIsDefinition(d)

        o = dereference(d)
        self.assertIs(o, 42)

    def test_str(self):
        s = 'foobar'
        d = Definition(str, s)
        self.assertIsDefinition(d)

        o = dereference(d)
        self.assertIs(o, s)

    def test_unicode(self):
        s = u'foobar'
        d = Definition(unicode, s)
        self.assertIsDefinition(d)

        o = dereference(d)
        self.assertIs(o, s)

    def _test_iterable(self, t, args, expected=None, tester=None):
        src = t(*args)
        expected = expected or copy(src)
        tester = tester or self.assertEqual

        d = Definition(t, src)
        self.assertIsDefinition(d)

        o = dereference(d)
        self.assertIsInstance(o, t)
        tester(o, expected)

        return src, o

    def test_list(self):
        self._test_iterable(
            list, (
                ('foo', 'bar', ),
            ),
            tester=self.assertListEqual
        )

    def test_tuple(self):
        self._test_iterable(
            tuple, (
                ('foo', 'bar', ),
            ),
            tester=self.assertTupleEqual
        )

    def test_recursive_iterable(self):
        for t, tester in (
                (list, self.assertListEqual, ),
                (tuple, self.assertTupleEqual, ),
        ):
            self._test_iterable(
                t, (
                    ('foo', Definition(int, 42), 'bar', ),
                ),
                expected=t(('foo', 42, 'bar', )),
                tester=tester
            )
            self._test_iterable(
                t, (
                    ('foo', [Definition(int, 42)], 'bar', ),
                ),
                expected=t(('foo', [42], 'bar', )),
                tester=tester
            )

    def test_tuple_identity(self):
        self.skipTest('test_definition: DefinitionTestCase.test_tuple_identity is not implemented yet.')
        source, result = self._test_iterable(
            tuple, (
                ('foo', 'bar', ),
            ),
            tester=self.assertTupleEqual
        )
        self.assertIs(source, result)

        source, result = self._test_iterable(
            tuple, (
                ('foo', Definition(int, 42), 'bar', ),
            ),
            tester=self.assertTupleEqual
        )
        self.assertIsNot(source, result)


