from copy import copy
from unittest import TestCase
import StringIO
from lxml import etree

from rdc.dic.definition import Definition, dereference
from rdc.dic.reference import is_reference

def from_xml(xml):
    xml = etree.parse(StringIO.StringIO(xml))
    print repr(etree.tostring(xml, pretty_print=True))

class XmlDefinitionTestCase(TestCase):
    def assertIsDefinition(self, o):
        self.assertIsReference(o)
        self.assertIsInstance(o, Definition)

    def assertIsReference(self, o):
        self.assertTrue(is_reference(o))

    def test_integer(self):
        for xml in (
            '<int>42</int>',
            '<value type="int">42</value>',
            '<service factory="int">42</service>',
        ):
            d = from_xml(xml)



