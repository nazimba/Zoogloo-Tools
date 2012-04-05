#!/usr/bin/env python
# encoding: utf-8
"""
zLogger.py

Created by andy on 2007-12-13.
Copyright (c) 2007 Zoogloo LLC. All rights reserved.

Usage:

>>> import logging
>>> log = zLog(__name__)
>>> log.LogToSocket('localhost', logging.handlers.DEFAULT_TCP_LOGGING_PORT)
>>> log.info('tits')
>>> 
>>> lg = zLog('Arse', console=False, level=logging.DEBUG)
>>> lg.LogToFile('./test.log')
>>> lg.info('hole')
>>> lg.debug('arse')

"""

__version__ = '$Revision: 0 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2010-04-10 14:04 -0700 $'

import sys
import os

import logging
import logging.handlers

defaultFormatString = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
defaultLevel = logging.INFO

class zLog(object):
	"""
	Wrapper class around pythons builtin logging module.  Just makes it nice
	easy to setup.
	
	Usage:
	
	>>> from zLogger import zLog
	>>> log = zLog(__name__)
	>>> log.LogToFile()
	>>> log.LogToSocket('localhost')
	>>> log.info('arse')
	
	"""
	
	_logger = None
	_level = None
	_format = None
	
	
	def __init__(self, name, console=True, 
				  level=defaultLevel, format=defaultFormatString):
		'''
		Creates a logger
		
		@param console: Switch to create a console logger by default.
		@type  console: bool
		
		'''
		super(zLog, self).__init__()
		
		# store the level and format #
		self._level = level
		self._format = format

		# get the logger #
		self._logger = logging.getLogger(name)
		# set the level #
		self._logger.setLevel(level)
		
		# setup logging to a console automatically #
		if console: self.LogToConsole()
		
	def LogToConsole(self):
		'''log to a console'''
		# create a console handler #
		ch = logging.StreamHandler()
		ch.setLevel(self._level)
		# setup the formatter #
		formatter = logging.Formatter(self._format)
		ch.setFormatter(formatter)
		# add the handler to the logger #
		self._logger.addHandler(ch)
		
	def LogToFile(self, filename, level=None, format=None):
		'''log output to a file'''
		
		# make sure the path exists #
		dirname = os.path.dirname(filename)
		if dirname and not os.path.exists(dirname):
			raise zLogError, 'Unable to find path %s' % dirname
		
		# create the filehandler #	
		fh = logging.handlers.RotatingFileHandler(filename, 
										 mode='a', maxBytes=10485760, backupCount=4)
		
		# setup the formatter #
		logFormat = self._format
		if format: logFormat = format
		formatter = logging.Formatter(logFormat)
		fh.setFormatter(formatter)
		
		# setup the level #
		logLevel = self._level
		if level: logLevel = level
		fh.setLevel(level)
		
		# add the file handler to the logger #
		self._logger.addHandler(fh)
		
	def LogToSocket(self, host, port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
					level=None, format=None):
		"""send logs to a scoket with the SocketHandler.  
		Use the zLogListener.py to view the output.
		
		@param level:  logging level of logger.  Use constants in logging,
					   such as logging.DEBUG
		@type level:  int
		"""
		sh = logging.handlers.SocketHandler(host, port)
		
		# set the level #
		if level: sh.setLevel(level)
		
		# add the socket handler to the logger #
		self._logger.addHandler(sh)
		
	def LogToEmail(self):
		"""send logs to email with the SMTPHandler.	 Not yet implemented."""
		pass
		
	def LogToSystem(self):
		"""send logs to system logs with SysLogHandler and NTEventLogHandler.  Not yet implemented."""
		pass
		
	def LogToHTTP(self):
		"""send logs to web server with HTTPHandler.  Not yet implemented."""
		pass
		
	@property
	def info(self):
		return self._logger.info
	
	@property
	def warning(self):
		return self._logger.warning
		
	@property
	def warn(self):
		return self._logger.warning
		
	@property
	def error(self):
		return self._logger.error
		
	@property
	def debug(self):
		return self._logger.debug
		
	@property
	def critical(self):
		return self._logger.critical
		
	@property
	def exception(self):
		return self._logger.exception
		
	@property
	def setLevel(self):
		return self._logger.setLevel
		
	

def main():
	
	log = zLog(__name__)
	log.LogToSocket('localhost', logging.handlers.DEFAULT_TCP_LOGGING_PORT)
	log.info('tits')
	
	lg = zLog('Arse', level=logging.DEBUG, console=False)
	lg.LogToFile('./test.log')
	lg.info('hole')
	lg.debug()
	

if __name__ == '__main__':
	main()