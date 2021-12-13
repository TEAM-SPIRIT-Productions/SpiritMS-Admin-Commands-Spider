# Logger Module - Spirit Logger
# Business logic obtained from https://www.toptal.com/python/in-depth-python-logging
# This is a generic advanced logger to log the operations of the program, for debug purposes
import sys
import logging
from logging.handlers import TimedRotatingFileHandler


# Use a config file for these, in larger projects:
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
FORMATTER = logging.Formatter(LOG_FORMAT)
LOG_FILE = "spiritms_admin_commands_spider.log"


def get_console_handler():
	console_handler = logging.StreamHandler(sys.stdout)
	console_handler.setFormatter(FORMATTER)
	return console_handler


def get_file_handler():
	file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
	file_handler.setFormatter(FORMATTER)
	return file_handler


class NullHandler(logging.Handler):
	def emit(self, record):
		pass


def get_logger(logger_name):
	logger = logging.getLogger(logger_name)
	logger.setLevel(logging.INFO)  # better to have too much log than not enough
	
	# Use silent handler if you want to be able to turn logging on and off
	# h = NullHandler()  # Instantiate with a silent handler that doesn't return anything, since
	# logger.addHandler(h)  # the logger object from the logging module REQUIRES at least ONE handler
	
	# Use default handler in this method, to always have logging on by default:
	logger.addHandler(get_console_handler())
	logger.addHandler(get_file_handler())
	
	return logger


def shutdown_logger():
	logging.shutdown()