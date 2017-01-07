from rdc.dic.test import TestCase
from rdc.dic.loader.xml import SIMPLE_TYPES

class SimpleTypesTestCase(TestCase):
    def test_bool(self):
        t = SIMPLE_TYPES['bool']

        for v in 't', '1', 'True', 'on', 'yes':
            self.assertTrue(t(v))
            self.assertTrue(t(v.upper()))
        self.assertTrue(t(1))

        for v in 'f', '0', 'False', 'off', 'no':
            self.assertFalse(t(v))
            self.assertFalse(t(v.upper()))
        self.assertFalse(t(0))

        self.assertRaises(ValueError, t, 2)
        self.assertRaises(ValueError, t, 'foobar')

    def test_str(self):
        t = SIMPLE_TYPES['str']
        self.assertEqual(t('foobar'), 'foobar')
        self.assertEqual(t(3.14159), '3.14159')

    def test_int(self):
        t = SIMPLE_TYPES['int']
        self.assertIs(t(1), 1)
        self.assertIs(t('1'), 1)
        self.assertRaises(ValueError, t, 'foobar')

    def test_float(self):
        t = SIMPLE_TYPES['float']
        self.assertAlmostEqual(t('3.14159'), 3.14159)
        self.assertAlmostEqual(t(3.14159), 3.14159)
        self.assertRaises(ValueError, t, 'foobar')
