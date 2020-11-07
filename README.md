

This project implements a both multi-threads-safe and multi-process-safe logger named **dblogger** in python language.

dblogger main interfaces are in file: [smartlogger/utils.dblogger.py]
Its config file is :[smartlogger/conf/logger.conf],which contains serveral key configuration below:

    [handler_truncateTimedRotatingFileHandler]
    class=smartlogger.utils.logutils.truncate_timed_rotating_filehandler.TruncateTimedRotatingFileHandler
    args=("logs/app.log", 'm', 1, 3600)
    level=INFO
    formatter=fmt0

TruncateTimedRotatingFileHandler was a truncated time rotating file handler and it's useful.

You can try to run dblogger demo executable by run commands:
    python -m smartlogger.loggerdemo.simpleloggerdemo
    or 
    python -m smartlogger.utils.logutils.dbloggerdemo
  
under root directory of project. After run these commands, you will see the rotating log files under directory:[smartlogger/logs/app.log*].
