#!/usr/bin/python

from pgsql import *
import xmlrpclib

def new(classname, plpy, SD, user_id, service_id, quantity):
	return eval(classname)(plpy, SD, user_id, service_id, quantity)


def whip():
	q = Query("select config.get('webhosting_ip') as host")
	result = q.execute()[0]
	return result["host"]

def mainip():
        q = Query("select config.get('main_ip') as host")
        result = q.execute()[0]
        return result["host"]

def second_to_midnight():
	q = Query("select webhosting_helpers.seconds_to_midnight() as sec")
        return int(q.execute()[0]["sec"])

class AbstractClass:
	def abstract():
		import inspect
		caller = inspect.getouterframes(inspect.currentframe())[1][3]
		raise NotImplementedError(caller + ' must be implemented in subclass')

class User:
	def __init__(self,id):
		q = Query("select * from webhosting.domains where id = $1")
		q.bind(id,"integer")
		result = q.execute()[0]
		self.id = id
		self.domain = result["domain"]
		self.attached_domain = result["attached_domain"]
	def get_money(self):
		q = Query("select balance from webhosting.accounts where id = $1")
		q.bind(self.id, "integer")
		return q.execute()[0]
	def alter_money(self,amount):
		q = Query("update webhosting.accounts set balance = balance + ($1) where id = $2")
		q.bind(amount, "real")
		q.bind(self.id, "integer")
		q.execute()

class Service:
	def __init__(self,id):
		q = Query("select * from webhosting.services where id = $1")
		q.bind(id,"integer")
		result = q.execute()
		if result.nrows() == 0:
			raise "No service with id %s!" % str(id)
		result = result[0]
		self.id = id
		self.cost = result["cost"]
		self.duration = result["duration"]
		self.pyclass = result["pyclass"]

COST_MUL = 30 * 24 * 60 * 60


class OxService(AbstractClass):
	def __init__(self, plpy, SD, user_id, service_id, quantity, write_off_f, expiration_date):
		QueryPlanner(plpy,SD)
		self.user = User(user_id)
		self.service = Service(service_id)
		self.write_off_f = write_off_f
		if not self.service.pyclass:
			raise "No pyclass specified for service with id %s!" % str(self.service.id)
		narrowed_class = eval(self.service.pyclass)(quantity)
		narrowed_class.user = self.user
		narrowed_class.service = self.service
		self.install_s = narrowed_class.install
		self.deinstall_s = narrowed_class.deinstall
	def install(self):
		if self.write_off_f:
			self.write_off()
		self.install_s()
	def deinstall(self):
		if self.write_off_f:
			self.money_back()
		self.deinstall_s()
	def write_off(self):
		secs = second_to_midnight()
		sec_cost = self.service.cost / COST_MUL
		amount = secs * sec_cost
		user_money = self.user.get_money()
		if user_money < amount:
			raise "Not enough money. User with id %s has %s on his account. This service will cost him %s." % \
				(self.user.id,user_money,amount)
		self.user.alter_money(-amount)
	def money_back(self):
		secs = second_to_midnight()
		sec_cost = self.service.cost / COST_MUL
		amount = secs * sec_cost
		self.user.alter_money(amount)

###### User classes ######



class RemoveAd(OxService):
	def __init__(self,quantity):
		self.proxy = xmlrpclib.ServerProxy("http://%s:1979/" % mainip())
	def install(self):
		self.proxy.oxserviced_reload()
	def deinstall(self):
		self.proxy.oxserviced_reload()


SPACE_AMOUNT=100
MB=1024*1024
class SpaceService(OxService):
	def __init__(self,quantity):
		self.proxy = xmlrpclib.ServerProxy("http://%s:1979/" % whip())
	def recheck_quotas(self):
		self.proxy.recheck_quotas(self.user.id)

class MoreDiskSpace(SpaceService):
	def __init__(self, quantity):
		SpaceService.__init__(self, quantity)
		self.quantity = quantity
	def install(self):
		q = Query("update webhosting.quotas set disk_max_size=disk_max_size+$1 where id=$2")
		q.bind(self.quantity*SPACE_AMOUNT*MB,"integer")
		q.bind(self.user.id,"integer")
		q.execute()
		#self.recheck_quotas()
	def deinstall(self):
		q = Query("update webhosting.quotas set disk_max_size=disk_max_size-$1 where id=$2")
		q.bind(self.quantity*SPACE_AMOUNT*MB,"integer")
		q.bind(self.user.id,"integer")
		q.execute()
		#self.recheck_quotas()


class MoreDbSpace(SpaceService):
	def __init__(self, quantity):
		SpaceService.__init__(self, quantity)
		self.quantity = quantity
	def install(self):
		q = Query("update webhosting.quotas set mysql_max_size=mysql_max_size+$1 where id=$2")
		q.bind(self.quantity*SPACE_AMOUNT*MB,"integer")
		q.bind(self.user.id,"integer")
		q.execute()
		#self.recheck_quotas()
	def deinstall(self):
		q = Query("update webhosting.quotas set mysql_max_size=mysql_max_size-$1 where id=$2")
		q.bind(self.quantity*SPACE_AMOUNT*MB,"integer")
		q.bind(self.user.id,"integer")
		q.execute()
		#self.recheck_quotas()

class NoRemove(OxService):
	def __init__(self, quantity):
		pass
	def install(self):
		pass
	def deinstall(self):
		pass

