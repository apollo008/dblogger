# -*- coding: utf-8 -*-
# @Time    : 2020/11/8 0:46
# @Author  : dingbinthu@163.com

from smartlogger.utils.logutils.dblogger import DBLoggingWrapper, DBLoggingProcess
import time


def curTimeStr():
    import datetime
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def main():
    loggerWrapper = DBLoggingWrapper()
    loggerProcess = DBLoggingProcess(loggerWrapper, ignore_signum=None, name='LoggerProcess')
    loggerProcess.start()

    count = 0
    while count < 600:
        loggerWrapper.getLogger().info(curTimeStr())
        time.sleep(1)

    loggerProcess.join()


if __name__ == '__main__':
    main()
