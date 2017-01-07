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
import io


class IResource(object):
    def __enter__(self):  # pragma: no cover
        raise NotImplementedError('Abstract.')

    def __exit__(self, *exc):  # pragma: no cover
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


class StringResource(io.StringIO):
    def __init__(self, buffer=None, namespace=None):
        io.StringIO.__init__(self, buffer)
        self.namespace = namespace

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False
