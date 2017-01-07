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

import logging

logger = logging.getLogger('rdc.dic')
_handler = logging.StreamHandler()
_formatter = logging.Formatter('%(asctime)s %(name)s:%(levelname)s %(message)s')
_handler.setFormatter(_formatter)
logger.addHandler(_handler)

LoggerAware = type('LoggerAware', (object,), {'logger': logger})

__all__ = [logger, LoggerAware]
