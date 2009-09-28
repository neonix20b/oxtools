#!/usr/bin/env python

"""PostgreSQL convenience module."""


class QueryPlanner(object):
        plpy = None
        SD = None
        def __init__(self,plpy,SD):
                QueryPlanner.plpy = plpy
                QueryPlanner.SD = SD
        def prepare(query, types):
                plan = None
                plan_key = "query_plan_" + query
                if QueryPlanner.SD.has_key(plan_key):
                        plan = QueryPlanner.SD[plan_key]
                else:
                        plan = QueryPlanner.plpy.prepare(query,types)
                        QueryPlanner.SD[plan_key] = plan
                return plan
        def execute(plan, values):
                return QueryPlanner.plpy.execute(plan, values)
        prepare = staticmethod(prepare)
	execute = staticmethod(execute)


class Query(object):
        def __init__(self,query):
                self.query = query
                self.plan = None
                self.values = []
                self.types = []
        def bind(self, value, type):
                self.values.append(value)
                self.types.append(type)
        def execute(self):
                if self.plan == None:
                        self.plan = QueryPlanner.prepare(self.query,self.types)
                return QueryPlanner.execute(self.plan,self.values)
        def clear(self):
                self.types = []
                self.values = []

def lock_ex(res):
	q = Query("select pg_advisory_lock($1)")
	q.bind(res,"integer")
	q.execute()

def unlock_ex(res):
	q = Query("select pg_advisory_unlock($1)")
        q.bind(res,"integer")
        q.execute()


def lock_sh(res):
        q = Query("select pg_advisory_lock_share($1)")
        q.bind(res,"integer")
        q.execute()

def unlock_sh(res):
        q = Query("select pg_advisory_unlock_share($1)")
        q.bind(res,"integer")
        q.execute()





