# -*- coding: utf-8 -*-

import io
import os
import StringIO

class IResource(object):
    def __enter__(self): # pragma: no cover
        raise NotImplementedError('Abstract.')

    def __exit__(self, *exc): # pragma: no cover
        raise NotImplementedError('Abstract.')

class FilesystemResource(object):
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


class StringResource(StringIO.StringIO):
    def __init__(self, buffer=None, namespace=None):
        StringIO.StringIO.__init__(self, buffer)
        self.namespace = namespace

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


