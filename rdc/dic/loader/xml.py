# -*- coding: utf-8 -*-
import sys
from rdc.dic.definition import Definition

import re

from collections import OrderedDict
from lxml import etree

def SERVICE(factory):
    pass

T_SERVICE = type('service', (object, ), {})
T_REFERENCE = type('reference', (object, ), {})

def _bool(v):
    v = v.lower()
    if v in ('t', '1', 'true', 'on', 'yes', ):
        return True
    elif v in ('f', '0', 'false', 'off', 'no', ):
        return False
    else:
        raise TypeError('Invalid boolean value {0}.'.format(repr(v)))

def _tuple(*p, **k):
    if len(k):
        raise ValueError('Cannot create tuple using keyword arguments.')
    return tuple(p)

def _list(*p, **k):
    if len(k):
        raise ValueError('Cannot create tuple using keyword arguments.')
    return list(p)

SIMPLE_TYPES = {
    'bool': _bool,
    'str': unicode,
    'int': int,
    'float': float,
}
COMPOSED_TYPES = {
    'tuple': _tuple,
    'list': _list,
}

def print_xml(node):
    import textwrap
    print(node)
    print(textwrap.dedent(etree.tostring(node, pretty_print=True)))

def _xml_text(node, strip=False, separator=None):
    text = [node.text]
    for child in node:
        if child.tail is not None:
            text.append(child.tail)
    text = filter(None, text)
    if strip:
        # strip
        text = map(lambda s: s.strip(), text)
        # remove empty strings
        text = filter(lambda s: len(s), text)
        separator = separator or ' '
    if len(text):
        return unicode((separator or '').join(text))
    return None

def _children_iterator(node, allowed=()):
    for child in node:
        if type(child) == etree._Comment:
            continue

        if not child.tag in allowed:
            raise ValueError('Unexpected tag "{0}".'.format(child.tag))

        yield child


class Loader(object):
    def __init__(self, container, locator):
        """
        :type container: rdc.dic.container.Container
        :type locator: rdc.dic.config.locator.IResourceLocator
        """
        self.container = container
        self.locator = locator

    def load(self, name, current_path=None):
        """
        Load external configuration into ``self.container``, resolving names using ``self.locator``.

        :type name: str
        """
        raise NotImplementedError('Abstract.')


class XmlLoader(Loader):
    NS = 'http://rdc.li/schema/rdc.dic/container'

    def load(self, name, current_path=None):
        file = self.locator.locate(name, current_path=current_path)[0]

        with self.locator.filesystem.open(file) as resource:
            node = etree.parse(resource)
            return self.parse(resource, node.getroot())

    def parse(self, resource, node, allowed=None):
        result = list(), OrderedDict(), list()

        allowed_children = ('service', 'value', 'import', 'int', 'str', 'reference', 'tuple' )
        if allowed:
            allowed_children += allowed

        for child_node in _children_iterator(node, allowed=allowed_children):
            parser = self.parse_node

            positional_arguments, keyword_arguments, special = parser(resource, child_node)

            if positional_arguments:
                result[0].extend(positional_arguments)
            if keyword_arguments:
                result[1].update(keyword_arguments)
            if special:
                result[2].extend(special)

        return result

    def parse_node(self, resource, node):
        _id = node.attrib.get('id', None)
        _hid = id or '(anonymous)'

        # retrieve type
        tag = node.tag.lower()
        if 'value' == tag:
            _type = node.attrib.get('type', '').lower()
            if '' == _type:
                # default to string
                _type = 'str'
        else:
            _type = tag

        if _type == T_SERVICE.__name__:
            _type = T_SERVICE
        elif _type == T_REFERENCE.__name__:
            _type = T_REFERENCE

        _children = (child for child in node)

        # build
        if _type in SIMPLE_TYPES:
            _value = self.__as_simple(SIMPLE_TYPES[_type], node)
        elif _type in COMPOSED_TYPES:
            _value = self.__as_composed(COMPOSED_TYPES[_type], node)
        elif _type is T_SERVICE:
            _value = self.__as_service(node)
        elif _type is T_REFERENCE:
            _value = None
        else:
            raise TypeError('Unknown type {0}.'.format(_type))

        # "key" attribute determines if this value is positional or keyword based.
        _key = node.attrib.get('key', None)
        if _key:
            _pv, _kv, _sv = None, {_key: _value}, None
        else:
            _pv, _kv, _sv = [_value], None, None

        # if "id" attribute is provided, setup in container
        if _id:
            try:
                self.container.set(_id, _value)
            except Exception as e:
                et, ex, tb = sys.exc_info()
                raise type(e), '{1} (while defining service "{0}").'.format(_hid, e.message), tb

        return _pv, _kv, _sv

    def __as_simple(self, typeof, node):
        value = _xml_text(node, strip=True)
        if value is not None:
            value = re.sub('%([a-z.-]+)%', lambda m: self.container.get(m.group(1)), value)
            return typeof(value)
        return None

    def __as_composed(self, typeof, node):
        text = _xml_text(node, strip=True)
        if text and len(text):
            raise ValueError('Composed types cannot have a text value (got {0!r}).'.format(text))

        p, k, s = self.parse(None, node)
        return typeof(*p, **k)

    def __as_service(self, node):
        text = _xml_text(node, strip=True)
        if text and len(text):
            raise ValueError('Services cannot have a text value (got {0!r}).'.format(text))

        factory_path = node.attrib.get('factory', None)
        if not factory_path:
            raise ValueError('Services must have a "factory" attribute.')

        p, k, s = self.parse(None, node)
        definition = Definition(factory_path, *p, **k)

        for st, sp, sk in s:
            definition.add(st, *sp, **sk)

        return definition


