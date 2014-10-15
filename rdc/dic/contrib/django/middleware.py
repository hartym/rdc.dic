# -*- coding: utf-8 -*-

from rdc.dic import Container
from rdc.dic.scope import NamespacedScope

class ContainerMiddleware:
    """

    """

    def __init__(self):
        # Import it in constructor instead of module so it won't fail at import even if django is not installed.
        from django.conf import settings
        from django.utils.module_loading import import_string

        try:
            c = settings.DI_CONTAINER
        except AttributeError as e:
            c = 'rdc.dic.Container'

        # Do I have to import it myself ?
        if isinstance(c, basestring):
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
        self.container.scopes['request'].leave(self.namespace(request))
        request.container = None
        return response







