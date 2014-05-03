# -*- coding: utf-8 -*-

from rdc.dic.config.filesystem import FilesystemImpl


class IResourceLocator(object):
    filesystem = FilesystemImpl

    def locate(self, name, current_path = None, first = True):
        raise NotImplementedError('Abstract.')


class ResourceLocator(IResourceLocator):
    def __init__(self, paths = None, filesystem = None):
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

