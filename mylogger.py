import logging, os
from logging.handlers import RotatingFileHandler

class Logger:
    def __init__(self, filename, backupCount=10, maxBytes=10*1024*1024):
        filename += '.log'
        if os.path.exists(filename):
            os.remove(filename)
        log_formatter = logging.Formatter(
            '%(asctime)s %(name)s %(funcName)s %(levelname)s (%(lineno)d) %(message)s'
        )
        my_handler = RotatingFileHandler(
            filename,
            mode='a',
            maxBytes=maxBytes,
            backupCount=backupCount,
            encoding='utf-8',
            delay=0
        )
        my_handler.setFormatter(log_formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(log_formatter)
        self.logger = logging.getLogger()
        self.logger.addHandler(my_handler)
        self.logger.addHandler(stream_handler)
        self.logger.setLevel(logging.INFO)

    def info(self, msg):
        self.logger.info(msg)

    def warn(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def critical(self, msg):
        self.logger.critical(msg)

    def setLevel(self, level):
        self.logger.setLevel(level)
