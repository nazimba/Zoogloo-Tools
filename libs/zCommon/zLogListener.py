#!/usr/bin/env python
# encoding: utf-8
"""
zLoggerServer.py

Created by andy on 2007-12-13.
Copyright (c) 2007 Zoogloo LLC. All rights reserved.

Pretty much a rip of: http://docs.python.org/lib/network-logging.html

"""

__version__ = '$Revision: 0 $'
__author__  = '$Author: andy $'
__date__    = '$Date: 2010-04-10 14:04 -0700 $'

import sys
import getopt

import cPickle
import logging
import logging.handlers
import SocketServer
import struct

# set up the global vars #
global LOG_FORMAT
global LOG_HOST
global LOG_PORT
LOG_HOST = 'localhost'
LOG_FORMAT = '%(clientHost)s %(asctime)s: [%(module)s] %(name)s - %(levelname)s: %(message)s'
LOG_PORT = logging.handlers.DEFAULT_TCP_LOGGING_PORT

class LogRecordStreamHandler(SocketServer.StreamRequestHandler):
	"""docstring for zLogSocketReceiver
	
	Added support in the log record for client host and client port.
	"""
	
	def handle(self):
		"""
		Handle multiple requests - each expected to be a 4-byte length,
		followed by the LogRecord in pickle format. Logs the record
		according to whatever policy is configured locally.
		"""
		while 1:
			chunk = self.connection.recv(4)
			if len(chunk) < 4:
				break
			slen = struct.unpack(">L", chunk)[0]
			chunk = self.connection.recv(slen)
			while len(chunk) < slen:
				chunk = chunk + self.connection.recv(slen - len(chunk))
			obj = self.unPickle(chunk)
			record = logging.makeLogRecord(obj)
			record.__dict__['clientHost'] = self.client_address[0]
			record.__dict__['clientPort'] = self.client_address[1]
			self.handleLogRecord(record)
			logging.LogRecord
		
	def unPickle(self, data):
		return cPickle.loads(data)

	def handleLogRecord(self, record):
		# if a name is specified, we use the named logger rather than the one
		# implied by the record.
		if self.server.logname is not None:
			name = self.server.logname
		else:
			name = record.name
		logger = logging.getLogger(name)
		# N.B. EVERY record gets logged. This is because Logger.handle
		# is normally called AFTER logger-level filtering. If you want
		# to do filtering, do it at the client end to save wasting
		# cycles and network bandwidth!
		logger.handle(record)

class LogRecordSocketReceiver(SocketServer.ThreadingTCPServer):
	"""simple TCP socket-based logging receiver suitable for testing.
	"""

	allow_reuse_address = 1

	def __init__(self, host='localhost',
				 port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
				 handler=LogRecordStreamHandler):
		# global LOG_PORT
		print 'Setting Receiver to: %s:%s' % (host, port)
		SocketServer.ThreadingTCPServer.__init__(self, (host, port), handler)
		self.abort = 0
		self.timeout = 1
		self.logname = None

	def serve_until_stopped(self):
		import select
		abort = 0
		while not abort:
			rd, wr, ex = select.select([self.socket.fileno()],
									   [], [],
									   self.timeout)
			if rd:
				self.handle_request()
			abort = self.abort
			
		


help_message = '''

---------------------------------
Zoogloo Log Listener
---------------------------------
USAGE:

    > zLogListener [options]

OPTIONS:
-f [--format]   Format for the logger in the python 
                logging.Formatter syntax

-n [--host]     address to listen on, default = 
                localhost

-p [--port]     Port to listen on, default = 
                logging.handlers.DEFAULT_TCP_LOGGING_PORT


'''


class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg


def main(argv=None):
	
	# get the global variables #
	global LOG_FORMAT
	global LOG_PORT
	global LOG_HOST

	if argv is None:
		argv = sys.argv
	try:
		try:
			opts, args = getopt.getopt(argv[1:], "hf:p:n:", ["help", "port=", "format=", "host="])
		except getopt.error, msg:
			raise Usage(msg)
	
		# option processing
		for option, value in opts:
			if option in ("-h", "--help"):
				raise Usage(help_message)
			if option in ('-f', '--format'):
				LOG_FORMAT = value
			if option in ('-p', '--port'):
				LOG_PORT = int(value)
			if option in ('-n', '--host'):
				LOG_HOST = value
	
	except Usage, err:
		print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		return 2

	###############################
	# run it 
	###############################
	try:
		logging.basicConfig(
			format=LOG_FORMAT)
		tcpserver = LogRecordSocketReceiver(host=LOG_HOST, port=LOG_PORT)
		print "Starting Logging server..."
		print "Listening on port: %s" % LOG_PORT
		print "Formatting with: %s" % LOG_FORMAT
		tcpserver.serve_until_stopped()
	except KeyboardInterrupt, e:
		tcpserver.abort = 1
		print '\nExiting Logger'

if __name__ == "__main__":
	sys.exit(main())
