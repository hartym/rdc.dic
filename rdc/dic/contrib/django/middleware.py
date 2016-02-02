# -*- coding: utf-8 -*-
import six
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
            container = settings.SERVICE_CONTAINER
        except (AttributeError, NameError) as e:
            try:
                container_class = settings.SERVICE_CONTAINER_CLASS
            except (AttributeError, NameError) as e:
                container_class = 'rdc.dic.Container'

            # If we got a string, import it.
            if isinstance(container_class, six.string_types):
                container_class = import_string(container_class)

            container = container_class()

        # If we got a string, import it.
        if isinstance(container, six.string_types):
            container = import_string(container)

        assert isinstance(container, Container), ('I tried my best to find your container but I got stuck. Either set '
                                                  'SERVICE_CONTAINER_CLASS to a container factory or SERVICE_CONTAINER '
                                                  'to a container instance. Thanks, bye.')

        self.container = container
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







