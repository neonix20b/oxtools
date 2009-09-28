#!/usr/bin/python
import threading
from syslog import *
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SocketServer import ThreadingMixIn
import os

class ThreadedXMLRPCServer(ThreadingMixIn,SimpleXMLRPCServer): pass

class RpcDaemon(threading.Thread):
    def __init__(self,ip,port):
    	threading.Thread.__init__(self)
	self.server = ThreadedXMLRPCServer(addr=(ip,port), allow_none=True)
    def export(self, function, export_name):
        self.server.register_function(function,export_name)
    def run(self):
        syslog(LOG_INFO, "RPC thread started")
	self.server.serve_forever()


