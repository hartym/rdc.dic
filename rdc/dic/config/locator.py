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

from rdc.dic.config.filesystem import FilesystemImpl


class IResourceLocator(object):
    filesystem = FilesystemImpl

    def locate(self, name, current_path=None, first=True):  # pragma: no cover
        raise NotImplementedError('Abstract.')


class ResourceLocator(IResourceLocator):
    def __init__(self, paths=None, filesystem=None):
        self.paths = paths or []
        self.filesystem = filesystem or self.filesystem

    def locate(self, name, current_path=None, first=True):
        if self.filesystem.is_absolute(name):
            if not self.filesystem.exists(name):
                raise IOError('The file "{0}" does not exist (using {1}).'.format(name, repr(self.filesystem)))
            return [name]

        resources = []

        paths = self.paths
        if current_path:
            paths = [current_path] + paths

        for path in paths:
            resource = self.filesystem.join(path, name)
            if self.filesystem.exists(resource):
                if first:
                    return [resource]
                if not resource in resources:
                    resources.append(resource)

        if not len(resources):
            raise IOError('The file "{0}" does not exist (using {1} with search paths {2}).'.format(
                name, repr(self.filesystem), ', '.join(paths)
            ))

        return resources
