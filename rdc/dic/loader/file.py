import io, os
from rdc.dic.definition import Definition
from lxml import etree
from rdc.dic import Container, debug_container
import sys
import re

def service_path_join(*args):
    p = ''
    for arg in args:
        if not arg or not len(arg):
            continue
        if not len(p):
            assert arg[0] != '.'
            p += arg
        else:
            if arg[0] == '.':
                p += arg
            else:
                p = arg
    return p

def _children_iterator(xml, allowed=()):
    for child in xml:
        if type(child) == etree._Comment:
            continue

        if not child.tag in allowed:
            raise ValueError('Unexpected tag "{0}".'.format(child.tag))

        yield child

def _bool_type(v):
    v = v.lower()
    if v in ('t', '1', 'true', 'on', 'yes', ):
        return True
    elif v in ('f', '0', 'false', 'off', 'no', ):
        return False
    else:
        raise TypeError('Invalid boolean value {0}.'.format(repr(v)))

VALUE_TYPES = [
    'bool', 'str', 'int', 'float', 'service',
]

ARGUMENT_TYPES = {
    'bool': _bool_type,
    'str': unicode,
    'int': int,
    'float': float,
}

class FileResource(object):
    def __init__(self, filename, mode, namespace=None):
        self.filename = filename
        self.dirname = os.path.dirname(filename)
        self.mode = mode
        self.file = None
        self.namespace = namespace

    def __enter__(self):
        self.file = io.open(self.filename, mode=self.mode, encoding='utf-8')
        return self.file

    def __exit__(self, *exc):
        self.file.close()
        self.file = None
        return False

class Locator(object):
    def __init__(self, path):
        self.path = path

    def get_reader(self, name, namespace=None, path=None):
        filename = os.path.join(*filter(None, (self.path, path, name, )))
        return FileResource(filename, mode='rU', namespace=namespace)

class Loader(object):
    def __init__(self, container, locator):
        self.container = container
        self.locator = locator

    def load(self, name, namespace=None, path=None):
        resource = self.locator.get_reader(name, namespace=namespace, path=path)
        with resource as io_stream:
            xml = etree.parse(io_stream)
            self.parse(resource, xml.getroot())

    def parse_import(self, resource, xml):
        assert xml.text is None
        assert 'resource' in xml.attrib
        name = xml.attrib['resource']
        import_as = xml.attrib.get('as', None)
        ignore_errors = bool(xml.attrib.get('ignore-errors', False))

        try:
            self.load(name, namespace='.'.join(filter(None, (resource.namespace, import_as))), path=resource.dirname)
        except Exception, e:
            if not ignore_errors:
                raise
                et, ex, tb = sys.exc_info()
                raise type(e), '{0} (while importing {1} as {2}).'.format(e.message, name, import_as), tb

    def parse_value(self, resource, xml):
        id = xml.attrib.get('id', None)

        # TYPE: cast value to correct type
        type = xml.attrib.get('type', 'str').lower()
        if type == 'service':
            value = self.container.ref(xml.attrib.get('id'))
        else:
            value = unicode(xml.text) if xml.text else u''
            value = re.sub('%([a-z.-]+)%', lambda m: self.container.get(service_path_join(resource.namespace, m.group(1))), value)
            value = ARGUMENT_TYPES[type](value)

        # ID: set in container if provided
        if id:
            self.container.set_parameter(service_path_join(resource.namespace, id), value, allow_override=True)

        # KEY: either positional or keyword argument
        if 'key' in xml.attrib:
            return {xml.attrib['key']: value}
        else:
            return [value]

    def parse_call(self, resource, xml):
        if not 'attr' in xml.attrib:
            raise ValueError('No target given for reference.')
        xml.attrib.get('attr')

        a, k = [], {}
        for element in _children_iterator(xml, allowed=('service', 'value', 'reference', )):
            _retval = getattr(self, 'parse_{0}'.format(element.tag))(resource, element)
            if element.tag != 'call':
                if type(_retval) == list:
                    a += _retval
                elif type(_retval) == dict:
                    k.update(_retval)
                else:
                    raise ValueError('Invalid')

    def parse_service(self, resource, xml):
        # ID
        id = xml.attrib.get('id', None)
        if id:
            id = service_path_join(resource.namespace, id)
            hid = id
        else:
            id = None
            hid = '(anonymous service)'

        # FACTORY: how to build, baby
        if 'factory' in xml.attrib:
            factory = xml.attrib.get('factory')
        else:
            raise ValueError('No factory defined for service "{0}".'.format(hid))

        # Children, if value returned use as factory injections
        a, k = [], {}
        for element in _children_iterator(xml, allowed=('service', 'value', 'reference', 'call',)):
            _retval = getattr(self, 'parse_{0}'.format(element.tag))(resource, element)
            if element.tag != 'call':
                if type(_retval) == list:
                    a += _retval
                elif type(_retval) == dict:
                    k.update(_retval)
                else:
                    raise ValueError('Invalid')

        service = Definition(factory, *a, **k)

        # ID: set in container if provided
        if id:
            try:
                self.container.define(id, service)
            except Exception as e:
                et, ex, tb = sys.exc_info()
                raise type(e), '{1} (while defining service "{0}").'.format(hid, e.message), tb

        # KEY: either positional or keyword argument
        if 'key' in xml.attrib:
            return {xml.attrib['key']: service}
        else:
            return [service]

    def parse_reference(self, resource, xml):
        # FOR: target id
        if not 'for' in xml.attrib:
            raise ValueError('No target given for reference.')
        ref = self.container.ref(xml.attrib.get('for'))

        if 'key' in xml.attrib:
            return {xml.attrib['key']: ref}
        else:
            return [ref]
        return

    def parse(self, resource, xml):
        for element in _children_iterator(xml, allowed=('service', 'value', 'import', )):
            getattr(self, 'parse_{0}'.format(element.tag))(resource, element)


