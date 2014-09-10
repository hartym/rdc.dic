# -*- coding: utf-8 -*-

def debug_container(container):
    for name in sorted(container.refs.keys()):
        yield name, container.ref(name), container.scope_of(name)

class ContainerInspector(object):
    def __init__(self, container):
        super(ContainerInspector, self).__init__()
        self.container = container

    def __iter__(self):
        for name in sorted(self.container.refs.keys()):
            yield name, self.container.ref(name), self.container.scope_of(name)

    def get_instances(self, name):
        pass

