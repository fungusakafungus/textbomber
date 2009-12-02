# vim: encoding=utf-8

import sqlite3
import random
import md5
import re
import logging

logger = logging.getLogger("dissociatedpress")
preferLogger = logging.getLogger("dissociatedpress.prefer")

class DissociatedPress(object):
    seed = None
    """Initial state (history) of the Markov chain"""

    order = 5
    """Initial order of the Markov chain used to generate text"""

    prefer = None

    _targetOrder = order

    max_order = 10

    _conn = None

    def __init__(self,dbfilename="default.sqlite"):
        self.filter=DissociatedPress.defaultFilter
        self.encoding = "utf-8"
        self._conn = sqlite3.connect(dbfilename)
        cur=self._conn.cursor()
        try:
            cur.execute("select * from data")
            cur.fetchone()
            #_debug(cur.fetchall())
            cur.execute("select * from meta")
            cur.fetchone()
            #_debug(cur.fetchall())
        except:
            self._createDB()
        finally:
            self._loadDB()

    def analyze(self,input,textId=0,optimize=True):
        """Analyzes (stores in a database) given string
        """
        input = self.filter(input)
        hash = md5.new(input.encode(self.encoding)).hexdigest()
        if self._hashLoaded(hash):
            raise Warning("input starting with '%s' \
                    is already in the database" % input[:10])
        if len(input)<self.max_order:
            raise Exception("input too short")

        self._deleteIndexes()

        input += input[:self.max_order]

        data = []
        for i in range(len(input)-self.max_order):
            str=input[i:i+self.max_order+1]
            data += [[textId] + [c for c in str]]

        sql = "insert into data(text_id"
        for i in xrange(self.max_order+1):
            sql += ", c%i" % i
        sql += ") values ("
        sql += "?,"*(self.max_order + 1) + "?)"

        self._conn.executemany(sql,data)
        if optimize:
            self.optimize()
        self._storeHash(hash)
        self._conn.commit()
        self._trySetInitialSeed()
        self.prefer = textId

    def optimize(self):
        sql = "create index i%s on data(" % self.max_order
        for i in xrange(self.max_order+1):
            sql += "c%i" % i
            if i < self.max_order: sql += ","
        sql += ")"
        self._conn.execute(sql)

    def peek(self,prefer=None):
        """Returns next character based on current chain settings"""
        
        sql = "select c%i from (select c%i from data where 1=1 " % (self.order,self.order)
        if prefer != None:
            preferLogger.debug("preferring %i" % prefer)
            sql += "and text_id = '%i' " % prefer
        for i in range(self.order):
            sql +="and c%i=? " % i
        sql += " limit 100) order by random()"
        cur = self._conn.cursor()
        assert self.seed != None
        try:
            cur.execute(sql,[c for c in self.seed])
        except Exception, e:
            _debug( "execute(%s,%s)", (sql,[c for c in self.seed[:self.order]]))
            raise e

        row = cur.fetchone()
        if row == None:
            if prefer != None: # retry without 'prefer'
                preferLogger.debug("preferring %i failed, retrying" % prefer)
                return self.peek()
            else: 
                raise StopIteration("no next")
        nextchar = row[0]
        return nextchar

    def next(self):
        """Returns next character and advances seed"""

        nextchar = self.peek(self.prefer)
        if self.order == self._targetOrder:
            self.__dict__['seed'] = self.seed[1:]+nextchar
        elif self.order < self._targetOrder:
            self.__dict__['order'] = self.order + 1
            self.__dict__['seed'] = self.seed+nextchar
        else:
            raise RuntimeError("self.order(%s) > self._targetOrder(%s)" 
                    % (self.order, self._targetOrder))
        return nextchar

    def setOrder(self, order):
        if order > self.max_order:
            raise RuntimeError("order(%s) > max_order(%s)" 
                    % (order, self.max_order))
        if order < 1:
            raise RuntimeError("order < 1")
        old_order = self.order
        if order <= self.order:
            self.__dict__['order'] = order
            if self.seed and len(self.seed) != order:
                self.seed = self.seed[-order:]

        self._targetOrder = order

    def setSeed(self, seed):
        if len(seed) != self.order:
            raise RuntimeError("seed length(%s) != order(%s)" 
                    % (len(seed), self.order))

        self.__dict__['seed'] = seed

        # check seed
        old_seed = self.seed
        try:
            self.peek()
        except StopIteration, e:
            self.__dict__['seed'] = old_seed
            raise RuntimeError("bad seed(%s)" % seed)

    def defaultFilter(cls,input):
        return re.sub('[ 	\n]+',' ',input)
    defaultFilter = classmethod(defaultFilter)

    def _createDB(self):
        self._conn.isolation_level="DEFERRED"
        self._conn.execute("create table meta(name text, value text)")
        self._conn.execute("create table imported(hash text)")
        self._conn.execute(
            """insert into meta(name, value) 
                values ('max_order',?)""",
            [self.max_order])
        sql = "create table data(text_id int default 0,"
        for i in range(self.max_order+1):
            sql += "c%i char" % i
            if i < self.max_order: sql += ","
        sql += ")"
        self._conn.execute(sql)

    def _loadDB(self):
        cur=self._conn.cursor()
        cur.execute("select value from meta where name = 'max_order'")
        self.max_order=int(cur.fetchone()[0])
        cur.execute("select text_id from data limit 1")
        try:
            row = cur.fetchone()
            self.prefer = int(row[0])
        except:
            pass
        self._trySetInitialSeed()

    def _clearDB(self):
        self._conn.execute("delete from data")

    def _storeHash(self,hash):
        cur = self._conn.cursor()
        cur.execute('insert into imported(hash) values (?)',(hash,))

    def _hashLoaded(self,hash):
        cur = self._conn.cursor()
        cur.execute('select count(*) from imported where hash = ?',(hash,))
        res = cur.fetchone()
        _debug(type(res))
        _debug(res)
        return res[0] == 1

    def _deleteIndexes(self):
        cur = self._conn.cursor()
        cur.execute("""select name 
                from sqlite_master 
                where type = 'index' 
                order by name""")
        cur2 = self._conn.cursor()
        for row in cur.fetchall():
            cur2.execute("drop index %s" % row[0])

    def __setattr__(self,name,value):
        if name == 'order':
            self.setOrder(value)
        elif name == 'seed':
            self.setSeed(value)
        else:
            object.__setattr__(self, name, value)

    def _trySetInitialSeed(self):
        cur = self._conn.cursor()
        cur.execute("select * from data limit 1")
        row = cur.fetchone()
        try:
            self.__dict__['order'] = self.max_order
            self._targetOrder = self.order
            self.seed = ''.join(row[1:-1])
        except:
            pass

def _debug(*str):
    if 0:
        print str
