# -*- coding: utf-8 -*-
# @Time    : 2020/5/5 20:59
# @Author  : dingbinthu@163.com

from smartlogger.utils.logutils.dblogger import DBLoggingWrapper, DBLoggingProcess
import time
import sys
import os
import multiprocessing
import signal


def stopLoggerProcess(name,dbloggingWrapper,stopFlag,ignoreSignum):

    if ignoreSignum:
        import signal
        signal.signal(ignoreSignum, signal.SIG_IGN)

    logger = dbloggingWrapper.getLogger()
    logger.info('wait stopping dbloggingProcess from process:[%s]' % name)
    sec = 86400
    for x in range(sec):
        if stopFlag.value == 1:
            break
        logger.info('wait [%d] seconds to stop Logger process.' % (sec-x))
        time.sleep(1)
    dbloggingWrapper.setStopFlag()
    logger.info('Process:[%s(%d)] exit----' % (multiprocessing.current_process().name, os.getpid()))
    sys.exit(0)


class ProduceWorker(multiprocessing.Process):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None,dbloggingWrapper=None, stopFlag=None,ignoreSignum=None):
        super(ProduceWorker, self).__init__()
        self.name = name
        self.dbloggingWrapper = dbloggingWrapper
        self.stopFlag = stopFlag
        self.ignoreSignum = ignoreSignum

    def run(self):
        if self.ignoreSignum:
            import signal
            signal.signal(self.ignoreSignum, signal.SIG_IGN)

        logger = self.dbloggingWrapper.getLogger()
        while True:
            if self.stopFlag.value == 1:
                break
            logger.info('Hello World from process:[%s]' % self.name)
            time.sleep(1)
        logger.info('Process:[%s(%d)] exit----' % (multiprocessing.current_process().name, os.getpid()))
        sys.exit(0)



def main():
    """
    windows 下  CTRL+C 代替 LINUX下的 kill -INT pid 或者 kill -2 pid ,同时因为所有进程都会接受到kill -2 信号，如果只想要主进程接受到信号，而子进程忽略信号
    需要在子进程 操作如下：
    import signal
    signal.signal(2, signal.SIG_IGN)
    """
    signum = str(sys.argv[1])

    DBLoggingWrapper.writePid()
    dbloggingWrapper = DBLoggingWrapper()
    loggerProcess = DBLoggingProcess(dbloggingWrapper, name='DBLoggingProcess', ignore_signum=signum,)
    loggerProcess.start()

    logger = dbloggingWrapper.getLogger()


    stopFlag = multiprocessing.Value('i', 0)
    stopProcess = multiprocessing.Process(name='stopLoggerProcess', target=stopLoggerProcess, args=('stopLoggerProcess',dbloggingWrapper,stopFlag,signum))
    produceProcess = ProduceWorker(dbloggingWrapper=dbloggingWrapper,name='ProduceWorker',stopFlag=stopFlag,ignoreSignum=signum)


    def sig_handler(signum, frame):
        print('-------------------------------------------------------')
        logger.info('Process:%s(%d) receive signal:[%d] at [%s].' % (multiprocessing.current_process().name, os.getpid(), signum, time.asctime()))
        stopFlag.value = 1
        time.sleep(3)
        dbloggingWrapper.setStopFlag()
        produceProcess.join()
        stopProcess.join()
        loggerProcess.join()
        print('=========Main Process exit')
        sys.exit(0)


    signal.signal(signum, sig_handler)
    logger.info('Signal:%s was pre set to terminate current program:%s(pid:%d).' % (signum, multiprocessing.current_process().name, os.getpid()))

    stopProcess.start()
    produceProcess.start()

    # produceProcess.join()
    # stopProcess.join()
    # loggerProcess.join()

    while True:
        time.sleep(3)

    print('=========Main Process exit')

if __name__ == '__main__':
    main()
