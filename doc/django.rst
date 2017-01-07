Integration with Django
=======================

In django settings, add middleware on top:

.. code-block:: python

    MIDDLEWARE_CLASSES = ('rdc.dic.contrib.django.middleware.ContainerMiddleware', ) + MIDDLEWARE_CLASSES
