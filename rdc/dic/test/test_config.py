import os
from rdc.dic.config.filesystem import DictImpl
from rdc.dic.config.locator import ResourceLocator
from rdc.dic.test import TestCase

FILESYSTEM = DictImpl({
    '/not-config.xml': 'wrong',
    '/foo/config.xml': 'foo',
    '/bar/config.xml': 'bar',
    '/config.xml': 'root',
})

class ConfigTestCase(TestCase):
    def _build_locator(self, paths=None):
        return ResourceLocator(paths, filesystem=FILESYSTEM)

    def test_no_resolution_path_relative(self):
        l = self._build_locator()
        self.assertRaises(IOError, l.locate, 'config.xml')

    def test_absolute(self):
        l = self._build_locator()

        # test with /config.xml
        f = '/config.xml'
        r = l.locate(f, first=False)
        self.assertListEqual(r, [f])
        r2 = l.locate(f)
        self.assertEqual(r[0], r2[0])

        f = '/bar/config.xml'
        r = l.locate(f, first=False)
        self.assertListEqual(r, [f])
        r2 = l.locate(f)
        self.assertEqual(r[0], r2[0])

    def test_resolution_path(self):
        resolution_order = ['/bar', '/']
        l = self._build_locator(resolution_order)
        f = 'config.xml'
        r = l.locate(f, first=False)
        expected = map(lambda x: os.path.join(x, f), resolution_order)
        self.assertListEqual(r, expected)
        r2 = l.locate(f)
        self.assertEqual(r[0], r2[0])
