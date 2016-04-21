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

from rdc.dic import Container
from rdc.dic.scope import NamespacedScope


class ContainerMiddleware(object):
    """
    Attach a service container to django's request object, with a namespace that allows to scope service instances
    to a given request.

    Set "SERVICE_CONTAINER_CLASS" in your project's settings.py to a custom class path to customize the container factory.

    """

    def __init__(self):
        # Import it in constructor instead of module so it won't fail at import even if django is not installed.
        from django.conf import settings
        from django.utils.module_loading import import_string

        try:
            c = settings.SERVICE_CONTAINER_CLASS
        except (AttributeError, NameError) as e:
            c = 'rdc.dic.Container'

        # Do I have to import it myself ?
        if isinstance(c, str):
            c = import_string(c)

        # Not a container ? Maybe a container factory.
        if not isinstance(c, Container):
            c = c()

        assert isinstance(c, Container), 'I tried my best to find your container. Your turn.'

        self.container = c
        if not 'request' in self.container.scopes:
            self.container.scopes['request'] = NamespacedScope()

    def namespace(self, request):
        return str(id(request))

    def process_request(self, request):
        request.container = self.container
        self.container.scopes['request'].enter(self.namespace(request))
        return None

    def process_response(self, request, response):
        if hasattr(request, 'container'):
            self.container.scopes['request'].leave(self.namespace(request))
            delattr(request, 'container')

        return response
