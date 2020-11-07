# -*- coding: utf-8 -*-
# @Time    : 2020/5/5 20:29
# @Author  : dingbinthu@163.com

import threading
import logging
import logging.handlers
import logging.config
import multiprocessing
import os
import sys

class DBLoggingWrapper(object):
    """
    This class wrapps logging operation through multi-process by DingBin in 20200505
    用于logger在多个进程间传递的数据 能成功pickle 序列化和反序列化
    """
    _endFlag = 'f1fe3745-8035-4908-b456-569378e2044d'
    _loggerName = 'SafeLogger'
    _instance_lock = threading.Lock()
    _isinit = False

    def __new__(cls, *args, **kwargs):
        """
        multiprocessing.Process调用后pickle反序列化之前会被调用
        """
        if not hasattr(cls,'_instance'):
            with cls._instance_lock:
                if not hasattr(cls,'_instance'):
                    cls._instance = object.__new__(cls)
                    print('Here %s _instance:[%s] was newed at first in process:[%s(%d)]' % (__class__, cls._instance, multiprocessing.current_process().name, os.getpid()))
        return cls._instance

    def __init__(self):
        """
        multiprocessing.Process调用后pickle反序列化之前 "不" 会被调用!!!
        此处不应在__init__函数中加入初始化类成员变量的行为 否则不经意间的初始化会造成新开启进程中pickle反序列化的类对象被覆盖
        或者 通过类成员变量识别是初次初始化
        """
        if not self.__class__._isinit:
            with self.__class__._instance_lock:
                if not self.__class__._isinit:
                    self.__class__._isinit = True
                    super(self.__class__, self).__init__()
                    print('Here %s _instance:[%s] inits in process:[%s(%d)]' % (self.__class__, self, multiprocessing.current_process().name, os.getpid()))
                    self.m_q = multiprocessing.Queue()
                    self.m_stopFlag = multiprocessing.Value('i', 0)

    @staticmethod
    def getLoggerConfFile():
        logger_conf_file = os.path.join(os.getcwd(), 'conf', "logger.conf")
        return logger_conf_file

    @staticmethod
    def writePid():
        with open('pid', 'w') as f:
            f.write(str(os.getpid()) + '\n')

    #pickle序列化时会被调用 指明pickle序列化哪些对象成员，默认类成员是不pickle序列化的
    def __getstate__(self):
        return (self.m_q, self.m_stopFlag, self.__class__._isinit)

    #pickle反序列化时会被调用
    def __setstate__(self, state):
        self.m_q, self.m_stopFlag, self.__class__._isinit = state

    @classmethod
    def getEndFlag(cls):
        return cls._endFlag

    def getLogger(self):
        if not hasattr(self, '_outerUsedLogger'):
            with self._instance_lock:
                if not hasattr(self, '_outerUsedLogger'):
                    self._genOuterLogger()
        return self._outerUsedLogger

    def _getInnerLogger(self):
        if not hasattr(self, '_innerUsedLogger'):
            with self._instance_lock:
                if not hasattr(self, '_innerUsedLogger'):
                    self._genInnerLogger()
        return self._innerUsedLogger

    def getQueue(self):
        return self.m_q

    def setStopFlag(self):
        logger = self.getLogger()
        with self.__class__._instance_lock:
            import time
            self.m_stopFlag.value = 1
            time.sleep(1)
            logger.critical(self.__class__._endFlag)

    def isStop(self):
        with self.__class__._instance_lock:
            return self.m_stopFlag.value == 1

    def _genInnerLogger(self):
        LOGGER_CONF_FILE = self.__class__.getLoggerConfFile()
        print('------loading LOGGER_CONF_FILE:[%s] in process:[%s(%d)]' % (LOGGER_CONF_FILE, multiprocessing.current_process().name, os.getpid()))
        logging.config.fileConfig(LOGGER_CONF_FILE)
        self._innerUsedLogger = logging.getLogger(self.__class__._loggerName)

    def _genOuterLogger(self):
        tlogger = logging.getLogger('OuterUsedSafeLogger')
        tlogger.setLevel(logging.DEBUG)
        tlogger.propagate = False
        queueHandler = logging.handlers.QueueHandler(self.m_q)
        queueHandler.setLevel(logging.DEBUG)

        # fmt = '[%(asctime)s] [%(msecs)d,%(filename)s:%(lineno)d -- %(funcName)s() %(levelname)s] [%(message)s]'
        # fmt = '[%(asctime)s] [%(msecs)d,process(%(process)d),thread(%(thread)d),%(filename)s:%(lineno)d -- %(funcName)s() %(levelname)s] [%(message)s]'
        fmt = '%(message)s'
        datefmt = '%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
        queueHandler.setFormatter(formatter)
        tlogger.addHandler(queueHandler)
        self._outerUsedLogger = tlogger



class DBLoggingProcess(multiprocessing.Process):

    def __init__(self, dbloggingWrapper, ignore_signum=None, name=None, daemon=None):
        super(DBLoggingProcess, self).__init__(name=name, daemon=daemon)
        self.dbloggingWrapper = dbloggingWrapper
        self.ignore_signum = ignore_signum

    def run(self):
        if self.ignore_signum:
            import signal
            signal.signal(self.ignore_signum, signal.SIG_IGN)

        innerLogger = self.dbloggingWrapper._getInnerLogger()
        innerLogger.info("[%s] from process:[%s(%d)] started..." % (self.__class__.__name__, multiprocessing.current_process().name, os.getpid()))
        while True:
            try:
                record = self.dbloggingWrapper.getQueue().get(block=True, timeout=1)
                if self.dbloggingWrapper.isStop() and record.msg == self.dbloggingWrapper.__class__.getEndFlag():
                    innerLogger.warning("[%s] from process:[%s(%d)] meet end flag and will stop..." % (self.__class__.__name__, multiprocessing.current_process().name, os.getpid()))
                    break
                if record:
                    innerLogger.handle(record)
            except multiprocessing.queues.Empty as e:
                innerLogger.debug("[%s] from process:[%s(%d)] meet empty queue timeout and will continue get from queue." % (self.__class__.__name__, multiprocessing.current_process().name, os.getpid()))
                pass
            except:
                import traceback
                innerLogger.error("[%s] from process:[%s(%d)] got exception:[%s] and will stop!!!" % (self.__class__.__name__, multiprocessing.current_process().name, os.getpid(), traceback.format_exc()))
                break
        innerLogger.info("===========[%s] from process:[%s(%d)] stopped right now!!!" % (self.__class__.__name__, multiprocessing.current_process().name, os.getpid()))
        sys.exit(0)


