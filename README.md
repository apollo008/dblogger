## Dblogger:  a powerful Python library supporting multi process and multi thread printing logs

This project implements a both multi-threads-safe and multi-process-safe logger library named **dblogger** in python language.  It works well and has stable function and powerful performance,especially in multithreaded or multiprocessed Python programs.



Main interfaces of **dblogger** are implemented in file:   **smartlogger/utils.dblogger.py** .

**dblogger** configuration file is:    **smartlogger/conf/logger.conf**. 

The **dblogger** configuration file has the following format:

    [loggers]
    keys=root,SafeLogger
    
    [handlers]
    keys=consoleHandler,fileHandler,rotatingFileHandler,timedRotatingFileHandler,truncateTimedRotatingFileHandler
    
    [formatters]
    keys=fmt0
    
    [logger_root]
    level=INFO
    handlers=consoleHandler
    
    [logger_SafeLogger]
    level=INFO
    #handlers=consoleHandler,truncateTimedRotatingFileHandler
    handlers=truncateTimedRotatingFileHandler
    qualname=SafeLogger
    propagate=0
    
    [handler_consoleHandler]
    class=StreamHandler
    args=(sys.stdout,)
    level=INFO
    formatter=fmt0
    
    [handler_fileHandler]
    class=FileHandler
    args=("logs/app.log", "a")
    level=INFO
    formatter=fmt0
    
    [handler_rotatingFileHandler]
    class=handlers.RotatingFileHandler
    args=("logs/app.log", 'a',100*1024*1024, 100)
    level=INFO
    formatter=fmt0
    
    
    [handler_timedRotatingFileHandler]
    class=handlers.TimedRotatingFileHandler
    args=("logs/app.log", 'm', 1, 3600)
    level=INFO
    formatter=fmt0
    
    [handler_truncateTimedRotatingFileHandler]
    class=smartlogger.utils.logutils.truncate_timed_rotating_filehandler.TruncateTimedRotatingFileHandler
    args=("logs/app.log", 'm', 1, 3600)
    level=INFO
    formatter=fmt0
    
    
    
    [formatter_fmt0]
    format=[%(asctime)s] [%(msecs)d,process(%(process)d),thread(%(thread)d),%(filename)s:%(lineno)d -- %(funcName)s() %(levelname)s] [%(message)s]
    datefmt=%Y-%m-%d %H:%M:%S
    

**TruncateTimedRotatingFileHandler**  was so important that it implements the following features: every few minutes or hours, it generates the log file name with a specific meaning, and then outputs the log content to the log file with the corresponding name. It was a truncated time rotating file handler and it's so useful.

You can run **dblogger** demo examples like this: 

```
python -m smartlogger.loggerdemo.simpleloggerdemo
python -m smartlogger.utils.logutils.dbloggerdemo
```

Then you will see the rotating log files generated under directory: **smartlogger/logs** after run above demo commands. And the  log file names may be like: **app.log** and **app.log.2020-11-08_01-01** and so on.

Please contact dingbinthu@163.com for related questions and other matters not covered. Enjoy it.



