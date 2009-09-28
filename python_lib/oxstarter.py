#!/usr/bin/python
import signal, os, sys
import os.path
from syslog import *

daemon = None
try:
	import daemon
except:
	import oxrpc
	daemon = oxrpc.remoteImport('daemon')

pidfile = None

def cleanup(signum, frame):
	os.unlink(pidfile)

def starter(fpid):
	if fpid.find('.pid') == -1: fpid = fpid + '.pid'
	openlog(fpid.replace('.pid',''))
	fpid = os.getcwd()+'/'+fpid
	pidfile = fpid
	param = 'start'
	if len(sys.argv) > 1: param =  sys.argv[1]
	if(param == 'kill'):
		os.unlink(fpid)
		os.system("killall -9 %s"%fpid.replace('.pid',''))
		print("killall -9 %s"%fpid.replace('.pid',''))
		exit(0)
	if param == "stop" or param == "restart":
		if os.path.isfile(fpid):
			f=open(fpid,'r')
			pid = f.readline()
			os.system("kill -9 %s" % (pid))
			print("stoped %s" % (pid))
			f.close()
			os.unlink(fpid)
		else: print "is already stopped"
		if(param == "restart"): param = "start"
		if(param == "stop"): exit(0)
	if(param == 'start'):
		if os.path.isfile(fpid):
			syslog(LOG_INFO, "second start")
			print "already started"
			exit(0)
		else:
			print("starting")
			daemon.createDaemon()
			signal.signal(signal.SIGTERM, cleanup)
			f=open(fpid,'w+')
			f.write(str(os.getpid()))
			f.close()
