import textwrap
from rdc.dic.config.filesystem import DictImpl
from rdc.dic.config.locator import ResourceLocator
from rdc.dic.container import Container
from rdc.dic.definition import dereference
from rdc.dic.loader.xml import XmlLoader
from rdc.dic.test import TestCase

FILESYSTEM = DictImpl({
    '/simple.xml': textwrap.dedent('''
        <container>
            <value type="int">42</value>
            <value type="str">foo</value>
            <value key="company" type="str">Acme Corp.</value>
        </container>
    '''),
    '/simple2.xml': textwrap.dedent('''
        <container>
            <int>42</int>
            <str>foo</str>
            <str key="company">Acme Corp.</str>
        </container>
    '''),
    '/tuple.xml': textwrap.dedent('''
        <container>
            <tuple>
                <int>1</int>
                <str>foo</str>
            </tuple>
            <tuple>
                <int>2</int>
                <str>bar</str>
            </tuple>
            <tuple key="named">
                <int>3</int>
                <str>baz</str>
            </tuple>
            <tuple>
                <int>4</int>
                <str>boo</str>
            </tuple>
        </container>
    '''),
    '/tuple2.xml': textwrap.dedent('''
        <container>
            <tuple>
                <int>1</int>
                <tuple>
                    <int>2</int>
                    <tuple>
                        <int>3</int>
                        <str>boo</str>
                    </tuple>
                    <str>bar</str>
                </tuple>
                <str>foo</str>
            </tuple>
        </container>
    '''),
    '/lazyint.xml': textwrap.dedent('''
        <container>
            <service id="lazyint" factory="int">
                <int>42</int>
            </service>
        </container>
    '''),
    '/intref.xml': textwrap.dedent('''
        <container>
            <service id="lazyint" factory="int">
                <int>42</int>
            </service>
            <reference for="lazyint" />
        </container>
    ''')
})


class Loader2TestCase(TestCase):
    def test_tuple(self):
        loader = self.__build_loader()
        l, d, s = loader.load('tuple.xml')
        self.assertListEqual(l, [(1, 'foo', ), (2, 'bar', ), (4, 'boo', )])
        self.assertDictEqual(d, {'named': (3, 'baz',)})
        self.assertEqual(len(loader.container), 1)

    def test_tuple2(self):
        loader = self.__build_loader()
        l, d, s = loader.load('tuple2.xml')
        self.assertListEqual(l, [(1, (2, (3, 'boo', ), 'bar', ), 'foo', )])
        self.assertEqual(len(loader.container), 1)

    def test_lazyint(self):
        loader = self.__build_loader()
        l, d, s = loader.load('lazyint.xml')
        self.assertEqual(len(loader.container), 2)
        o = self.container.get('lazyint')
        self.assertIs(o, 42)

    def test_intref(self):
        loader = self.__build_loader()
        l, d, s = loader.load('intref.xml')
        self.assertIs(dereference(l[0]), 42)
        self.assertIs(dereference(l[1]), 42)

    def __build_loader(self):
        locator = ResourceLocator('/', filesystem=FILESYSTEM)
        self.container = Container()
        return XmlLoader(self.container, locator)

