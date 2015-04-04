# -*- coding: utf-8 -*-

# python std lib
import logging
import logging.config

log = logging.getLogger()


# Set the root logger to be silent so all code that uses the python logger
# will not print anything unless we want it to, then it should be specified
# in each test and reseted after that test
def _set_log_lv(level=1337, loggers=None):
    """ If no level is set then level will be so high all logging is silenced
    """
    if loggers is None:
        # If no additional loggers is specified then only apply to root logger
        log.setLevel(level)
        for handler in log.handlers:
            handler.level = level
    else:
        # If we have other logging instances specified apply to root logger and them
        if log not in loggers:
            loggers.append(log)

        for log_instance in loggers:
            log_instance.setLevel(level)
            for handler in log_instance.handlers:
                handler.level = level


# Initially silence all logging
_set_log_lv()
