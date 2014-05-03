# -*- coding: utf-8 -*-

import os
from rdc.dic.config.resource import FilesystemResource, StringResource

class FilesystemImpl(object):
    is_absolute = staticmethod(os.path.isabs)
    exists = staticmethod(os.path.exists)
    join = staticmethod(os.path.join)

    @classmethod
    def open(cls, path):
        return FilesystemResource(path, mode='rU')


class DictImpl(FilesystemImpl):
    def __init__(self, dict):
        self.dict = dict

    @staticmethod
    def is_absolute(path):
        return path.startswith('/')

    def exists(self, path):
        return path in self.dict

    def open(self, path):
        return StringResource(self.dict[path])

