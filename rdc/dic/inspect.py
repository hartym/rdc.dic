# -*- coding: utf-8 -*-
#
# Copyright 2012-2016 Romain Dorgueil
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
