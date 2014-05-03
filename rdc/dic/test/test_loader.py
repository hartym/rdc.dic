# -*- coding: utf-8 -*-

from lxml import etree
from rdc.dic.loader.xml import XmlLoader
from rdc.dic.test import TestCase


class LoaderTestCase(TestCase):
    """
    Simple parsing tests without using anything that depends on resource loading or on container.

    """

    def test_parse_string(self):
        loader = self.__build_loader()
        for keyed in (False, True):
            for xml in (
                    '<str {attrs}>Eat at Joe</str>',
                    '<value type="str" {attrs}>Eat at Joe</value>',
                    '<str {attrs}>Eat <!-- maybe --> at Joe</str>',
                    '<str {attrs}><!-- don\'t --> Eat at Joe</str>',
                    '''<str {attrs}>
                        Eat at Joe
                    </str>''',
            ):
                xml = xml.format(attrs=(keyed and 'key="MyKey"' or ''))
                node = etree.fromstring(xml)
                pv, kv, sv = loader.parse_node(None, node)

                if keyed:
                    self.assertIsNone(pv)
                    self.assertDictEqual(kv, {u'MyKey': u'Eat at Joe'})
                else:
                    self.assertListEqual(pv, [u'Eat at Joe'])
                    self.assertIsNone(kv)

    def test_parse_unicode(self):
        loader = self.__build_loader()
        for keyed in (False, True):
            for xml, expected in (
                    (u'<str {attrs}>Eat at Joe</str>', u'Eat at Joe', ),
                    (u'''<str {attrs}>
                        Eat at Joe
                    </str>''', u'Eat at Joe', ),
                    (u'''<str {attrs}>
                        ก ข ฃ ค ฅ ฆ ง จ ฉ ช ซ ฌ ญ ฎ ฏ ฐ ฑ ฒ ณ ด ต ถ ท ธ น บ ป ผ ฝ พ ฟ ภ ม ย ร ฤ ล ฦ ว ศ ษ ส ห ฬ อ ฮ ฯ
                    </str>''', u'ก ข ฃ ค ฅ ฆ ง จ ฉ ช ซ ฌ ญ ฎ ฏ ฐ ฑ ฒ ณ ด ต ถ ท ธ น บ ป ผ ฝ พ ฟ ภ ม ย ร ฤ ล ฦ ว ศ ษ ส ห ฬ อ ฮ ฯ', ),
            ):
                xml = xml.format(attrs=(keyed and 'key="MyKey"' or ''))
                node = etree.fromstring(xml)
                pv, kv, sv = loader.parse_node(None, node)

                if keyed:
                    self.assertIsNone(pv)
                    self.assertDictEqual(kv, {u'MyKey': expected})
                else:
                    self.assertListEqual(pv, [expected])
                    self.assertIsNone(kv)

    def test_parse_int(self):
        loader = self.__build_loader()
        for keyed in (False, True):
            for xml in (
                    '<int {attrs}>42</int>',
                    '<value type="int" {attrs}>42</value>',
                    '''<int {attrs}>
                        42
                    </int>''',
                    '''<int {attrs}>
                        <!-- Answer to the Ultimate Question of Life, the Universe, and Everything -->
                        42
                        <!-- Yes sir! -->
                    </int>''',
            ):
                xml = xml.format(attrs=(keyed and 'key="MyKey"' or ''))
                node = etree.fromstring(xml)
                pv, kv, sv = loader.parse_node(None, node)

                if keyed:
                    self.assertIsNone(pv)
                    self.assertDictEqual(kv, {u'MyKey': 42})
                else:
                    self.assertListEqual(pv, [42])
                    self.assertIsNone(kv)

            # check malformed integer definitions
            for xml in (
                    '<int {attrs}>4 2</int>',
                    '<int {attrs}>foo</int>',
            ):
                xml = xml.format(attrs=(keyed and 'key="MyKey"' or ''))
                node = etree.fromstring(xml)
                self.assertRaisesRegexp(ValueError, 'invalid literal', loader.parse_node, None, node)

    def test_parse_tuple(self):
        return self.__test_parse_iterable(tuple, TestCase.assertTupleEqual)

    def test_parse_list(self):
        return self.__test_parse_iterable(list, TestCase.assertListEqual)

    def __build_loader(self):
        return XmlLoader(None, None)

    def __test_parse_iterable(self, iter_type, tester):
        loader = XmlLoader(None, None)
        for keyed in (False, True):
            for xml, expected in (
                    ('<value type="{type}" {attrs}><int>42</int><str>foo</str></value>', (42, 'foo')),
                    ('<{type} {attrs}><int>42</int><str>foo</str></{type}>', (42, 'foo')),
                    ('<{type} {attrs}><str>foo</str><int>42</int></{type}>', ('foo', 42)),
                    ('''<{type} {attrs}>
                        <int>42</int>
                        <str>foo</str>
                    </{type}>''', (42, 'foo')),
                    ('''<{type} {attrs}>
                        <!-- foo -->
                        <int><!-- int -->42<!-- end of int --></int>
                        <!-- bar -->
                        <str><!-- string -->foo<!-- end of string --></str>
                        <!-- baz -->
                    </{type}>''', (42, 'foo')),
            ):
                xml = xml.format(attrs=(keyed and 'key="MyKey"' or ''), type=iter_type.__name__)
                expected = iter_type(expected)
                node = etree.fromstring(xml)
                pv, kv, sv = loader.parse_node(None, node)
                if keyed:
                    self.assertEqual(len(kv), 1)
                    self.assertIsNone(pv)
                    tester(self, kv['MyKey'], expected)
                else:
                    self.assertEqual(len(pv), 1)
                    self.assertIsNone(kv)
                    tester(self, pv[0], expected)

