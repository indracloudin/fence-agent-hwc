# Mock syslog module for Windows development environment
import logging

# Syslog constants
LOG_CRIT = 2
LOG_ERR = 3
LOG_WARNING = 4
LOG_INFO = 6
LOG_DEBUG = 7

def syslog(priority, message):
    """
    Mock syslog function that logs to Python's logging system
    """
    if priority <= LOG_ERR:
        logging.error(message)
    elif priority == LOG_WARNING:
        logging.warning(message)
    elif priority == LOG_INFO:
        logging.info(message)
    elif priority == LOG_DEBUG:
        logging.debug(message)
    else:
        logging.info(message)