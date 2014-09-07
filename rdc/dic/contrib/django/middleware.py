# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.module_loading import import_string
from rdc.dic import Container
from rdc.dic.scope import NamespacedScope


class ContainerMiddleware:
    """

    """

    def __init__(self):
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

    def process_request(self, request):
        request.container = self.container
        self.container.scopes['request'].current_namespace = id(request)
        return None

    def process_response(self, request, response):
        self.container.scopes['request'].current_namespace = None
        request.container = None
        return response







