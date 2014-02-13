# -*- coding: utf-8 -*-
#
# Copyright 2012-2014 Romain Dorgueil
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

from functools import partial

class _partial(partial):
    __reference__ = True

    def __repr__(self):
        return unicode(self.repr) if hasattr(self, 'repr') else repr(self.func)

def reference(mixed, *args, **kwargs):
    _repr = kwargs.pop('_repr', None)

    if callable(mixed):
        p = _partial(mixed, *args, **kwargs)
        if _repr:
            p.repr = _repr
        return p

    def _reference(value=mixed):
        return value
    _reference.__reference__ = True
    return _reference

