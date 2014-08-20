# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging

logger = logging.getLogger('rdc.dic')
_handler = logging.StreamHandler()
_formatter = logging.Formatter('%(asctime)s %(name)s:%(levelname)s %(message)s')
_handler.setFormatter(_formatter)
logger.addHandler(_handler)

LoggerAware = type('LoggerAware', (object, ), {'logger': logger})

__all__ = [logger, LoggerAware]

