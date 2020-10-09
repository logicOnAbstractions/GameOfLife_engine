import os
import logging
from utils import LOG_DIR

DEFAULT_FORMATTER = logging.Formatter('%(asctime)s - %(name)s:%(levelname)s - %(message)s')
os.environ["ENV"] = "development"
os.environ["LOG_LEVEL"] = "DEBUG"

def get_root_logger(loggername, filename=None):
    """
    :param loggername: obv.
    :param filename: name of file where we want to output if we want a file handler.
    :return: the logger object from logging

    **Usage:** From anywhere in the project
    from logger import logger

    ``LOG = logger.get_root_logger(os.environ.get('ROOT_LOGGER', 'root'), filename=log_file)``

    then juste do ``LOG.error(...), LOG.info(...)`` as you would with the original logging.info() etc.

    The updside being we have decoupled the code from the actual logging lib used.


    """

    # log lvl - by default related to the ENV values of env vars (development/production etc.)
    # can be overridden by LOG_LEVEL env vars. must match logging.LOG_LVL, e.g. "DEBUG", etc.
    logger = logging.getLogger(loggername)
    debug = os.environ.get('ENV', 'development') == 'development'
    log_lvl = os.environ["LOG_LEVEL"]
    if log_lvl:
        # they overrode the default for the ENV level, use that
        logger.setLevel(getattr(logging, log_lvl))
    else:
        logger.setLevel(logging.DEBUG if debug else logging.INFO)

    if len(logger.handlers)==0:
        logger.addHandler(get_stream_handler())
    if filename and len(logger.handlers)<2:
        logger.addHandler(get_file_handler(filename))
    return logger

# those are usefule so we can easily build handlers from naywhere if needed (testing logs etc)

def get_stream_handler(formatter=DEFAULT_FORMATTER):
    """ builds & returns a stream handler"""
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    return sh

def get_file_handler(filename="logs.log", formatter=DEFAULT_FORMATTER):
    """ builds & return a file handler based on parameters """
    fh = logging.FileHandler(os.path.join(LOG_DIR, filename))
    fh.setFormatter(formatter)
    return fh
