# -*- coding: utf-8 -*-

class AbstractError(NotImplementedError):
    """Abstract error is a convenient error to declare a method as "being left as an exercise for the reader."""

    def __init__(self, method):
        super(AbstractError, self).__init__(
            'Call to abstract method {class_name}.{method_name}(...): missing implementation.'.format(
                class_name=type(method.im_self).__name__,
                method_name=method.__name__,
            ))

