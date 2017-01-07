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
