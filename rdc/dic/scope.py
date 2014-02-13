# -*- coding: utf-8 -*-
#
# Copyright 2012-2014 Romain Dorgueil
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

import re
from rdc.dic.reference import reference

MODULE = re.compile(r"\w+(\.\w+)*$").match

class Scope(object):
    """
    Service scope that returns  a new instance for a given service each time get(service_name) is called.
    """

    def __init__(self, container=None):
        self.container = container
        self.definitions = {}

    def define(self, name, definition):
        """Create definition and return a callable getter."""
        self.definitions[name] = definition
        return self.ref(name, repr=definition)

    def build(self, name):
        """Create an instance."""
        return self.definitions[name]()

    def ref(self, name, repr=None):
        ref = reference(self.build, name)
        if repr is not None:
            ref.repr = repr
        return ref


class CachedScope(Scope):
    """
    Service scope that returns the same instance for a given service each time get(service_name) is called.
    """

    def __init__(self, container=None):
        super(CachedScope, self).__init__(container)
        self.services = {}

    def get(self, name):
        """Get in scope or build."""
        if not name in self.services:
            self.services[name] = self.build(name)
        return self.services[name]
