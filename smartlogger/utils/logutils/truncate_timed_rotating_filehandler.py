# -*- coding: utf-8 -*-
# @Time    : 2020/4/25 16:48
# @Author  : dingbinthu@163.com
# @File    : truncate_timed_rotating_filehandler.py

import time
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime


class TruncateTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False, atTime=None):
        super(TruncateTimedRotatingFileHandler, self).__init__(filename, when=when, interval=interval, backupCount=backupCount, encoding=encoding, delay=delay, utc=utc, atTime=atTime)
        self._truncate_begin_time()

    def _truncate_begin_time(self):
        if self.when == 'S':
            t = datetime.now().replace(microsecond=0)
            self.rolloverAt = self.computeRollover(t.timestamp())
        elif self.when == 'M':
            t = datetime.now().replace(second=0, microsecond=0)
            self.rolloverAt = self.computeRollover(t.timestamp())
        elif self.when == 'H':
            t = datetime.now().replace(minute=0, second=0, microsecond=0)
            self.rolloverAt = self.computeRollover(t.timestamp())
        elif self.when == 'D' or self.when == 'MIDNIGHT' or self.when.startswith('W'):
            t = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            self.rolloverAt = self.computeRollover(t.timestamp())
