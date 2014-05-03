from rdc.dic import Container
from rdc.dic.test import TestCase

class ConfigTestCase(TestCase):
    def setUp(self):
        self.container = Container()

    def test_set_parameter(self):
        self.assertRaises(KeyError, self.container.get, 'foo')
        self.container.set_parameter('foo', 'bar')
        self.assertEqual(self.container.get('foo'), 'bar')

    def test_set_parameters(self):
        self.container.set_parameters({
            'foo': 42,
            'bar': 43
        })
        self.assertListEqual(self.container.get_parameters('foo', 'bar'), [
            42, 43
        ])
        self.assertListEqual(self.container.get_parameters('bar', 'foo'), [
            43, 42
        ])
