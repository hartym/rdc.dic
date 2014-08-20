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

from unittest import TestCase as BaseTestCase
from rdc.dic.util import cached_property


class TestCase(BaseTestCase):
    def run(self, result=None):
        self.logger.debug('[test] '+type(self).__name__+'.'+self._testMethodName+'() ...')
        super(TestCase, self).run(result)

    @cached_property
    def logger(self):
        from rdc.dic.logging import logger
        return logger