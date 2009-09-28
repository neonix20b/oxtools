#!/usr/bin/env python

"""OxPanel support functions module."""

import os
from os import system
from os import sys
from subprocess import Popen,PIPE
import threading



ADV_TEMPLATE=0x0

class TimeoutError(Exception): pass

def timelimit(timeout,descr):
	def internal(function):
		def internal2(*args, **kw):
			class Calculator(threading.Thread):
				def __init__(self):
					threading.Thread.__init__(self)
					self.result = None
					self.error = None

				def run(self):
					try:
						self.result = function(*args, **kw)
					except:
						self.error = sys.exc_info()[0]

			c = Calculator()
			c.start()
			c.join(timeout)
			if c.isAlive():
				raise TimeoutError,descr
			if c.error:
				raise c.error
			return c.result
		return internal2
	return internal



def dns_to_string(rec):
	result = ""
	if rec["type"] == "SOA":
		result = "%s %s=>%s %s %s SOA %s %s %s %s %s %s %s\n" % \
		(rec["zone"],rec["host"],rec["id"],rec["host"],rec["ttl"],rec["data"],rec["resp_person"], \
		rec["serial"],rec["refresh"],rec["retry"],rec["expire"],rec["minimum"])
	elif rec["type"] == "NS" or rec["type"] == "A" or rec["type"] == "CNAME":
		result = "%s %s=>%s %s %s %s %s\n" % \
			(rec["zone"],rec["host"], rec["id"],rec["host"],rec["ttl"],rec["type"],rec["data"])
	elif rec["type"] == "MX":
		result = "%s %s=>%s %s %s %s %s %s\n" % \
		(rec["zone"],rec["host"],rec["id"],rec["host"],rec["ttl"],rec["type"],rec["mx_priority"],rec["data"])
	return result

@timelimit(5,"Execution timeout in update_dns")
def update_dns(filename, host):
	system("cat %s >> /tmp/dnsupdate" % filename) #Log
	system("cat %s | ssh root@%s '/usr/sbin/dlzbdbhpt'" % (filename, host))

@timelimit(5,"Execution timeout in restart_dns")
def restart_dns(host):
	system("ssh root@%s '/etc/init.d/named restart'" % host)

@timelimit(1,"Execution timeout in pwgen")
def pwgen(length):
	p1 = Popen(["/usr/bin/pwgen", str(length),"1"], stdout=PIPE)
	return p1.communicate()[0][:-1]

@timelimit(10,"Execution timeout in configure_hosting")
def configure_hosting(id,domain,password,mysql_password,host):
	commands = ""
	commands += "/usr/sbin/oxhosting/users.pl register_user %s %s %s;" % (id,domain,password)
	commands += "/usr/sbin/oxhosting/users.pl register_mysql %s %s;" % (id,mysql_password)
	system("ssh root@%s '%s'" % (host,commands))

@timelimit(30,"Execution timeout in install_soft")
def install_soft(host, id, domain, password, soft, folder):
	system("ssh root@%s '/usr/sbin/oxhosting/users.pl install_soft %d %s %s %s %s'" % (host, id, domain, password, soft, folder))

@timelimit(10,"Execution timeout in remove_hosting")
def remove_hosting(id,domain,host):
	commands=""
	commands += "/usr/sbin/oxhosting/users.pl unregister_mysql %s;" % id
	commands += "/usr/sbin/oxhosting/users.pl unregister_user %s %s;" % (id,domain)
	system("ssh root@%s '%s'" % (host,commands))
	system("~oxpanel/bin/setremove %s" % id)

@timelimit(5,"Execution timeout in reload_apache_config")
def reload_apache_config(host):
	system("ssh root@%s '/etc/init.d/apache2 reload'" % host)

@timelimit(30,"Execution timeout in update_pkg")
def update_pkg(host):
	system("ssh root@%s '/usr/sbin/oxhosting/pkg.pl'" % host)



SENDMAIL = "/usr/sbin/sendmail" # sendmail location

#@timelimit(10, "Execution timeout in sendmail")
def sendmail(reply_to, subject, send_to, content):
	p = os.popen("%s -t" % SENDMAIL, "w")
	p.write("Reply-to: %s\n" % reply_to)
	p.write("From: %s\n" % reply_to)
	p.write("To: %s\n" % send_to)
	p.write("Subject: %s\n" % subject)
	p.write("Content-type: text/plain; charset=\"utf8\"\n")
	p.write("\n") # blank line separating headers from body
	p.write(content)
	p.close()

