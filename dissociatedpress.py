# vim: encoding=utf-8

import sqlite3
import random


class DissociatedPress(object):
    seed = None
    """Initial state (history) of the Markov chain"""

    order = 5
    """Initial order of the Markov chain used to generate text"""

    max_order = 10

    _conn = None

    def __init__(self,dbfilename="default.sqlite"):
        try:
            self._conn = sqlite3.connect(dbfilename)
            cur=self._conn.cursor()
            self._conn.execute("select * from data")
            cur.fetchone()
            #_debug(cur.fetchall())
            self._conn.execute("select * from meta")
            cur.fetchone()
            #_debug(cur.fetchall())
        except:
            self._createDB()
        finally:
            self._loadDB()
        #self.order=property(self.order)

    def _createDB(self):
        self._conn.isolation_level="DEFERRED"
        self._conn.execute("create table meta(name text, value text)")
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
        self._trySetInitialSeed()

    def _clearDB(self):
        self._conn.execute("delete from data")

    def analyze(self,input):
        self._clearDB()
        if len(input)<self.max_order:
            raise Exception("input too short")

        input += input[:self.max_order]
            
        data = []
        for i in range(len(input)-self.max_order):
            str=input[i:i+self.max_order+1]
            data += [[c for c in str]]

        sql = "insert into data("
        for i in range(self.max_order+1):
            sql += "c%i" % i
            if i < self.max_order: sql += ","
        sql += ") values ("
        sql += "?,"*self.max_order + "?)"

        self._conn.executemany(sql,data)
        self._conn.commit()
        self._trySetInitialSeed()

    def _trySetInitialSeed(self):
        cur = self._conn.cursor()
        cur.execute("select * from data limit 1")
        row = cur.fetchone()
        try:
            self.__dict__['order']=self.max_order
            self.seed = ''.join(row[1:-1])
        except:
            pass

    def peek(self,prefer=None):
        """Returns next character based on current chain settings"""
        
        sql = "select c%i from (select c%i from data where 1=1 " % (self.order,self.order)
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
            raise StopIteration("no next")
        nextchar = row[0]
        return nextchar

    def next(self,prefer=None):
        """Returns next character and advances seed"""

        nextchar = self.peek()
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
        old_order = self.order
        if order <= self.order:
            self.__dict__['order'] = order
            if self.seed and len(self.seed) != order:
                self.seed = self.seed[-order:]

        self._targetOrder = order
#            while order > self.order:
#                nextchar = self.peek()
#                self.__dict__['order'] = self.order + 1
#                if self.seed and len(self.seed) != order:
#                    self.seed = self.seed + nextchar

    def setSeed(self, seed):
        #try:
        #    self.order = len(seed)
        #except RuntimeError, e:
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

    def __setattr__(self,name,value):
        if name == 'order':
            self.setOrder(value)
        elif name == 'seed':
            self.setSeed(value)
        else:
            object.__setattr__(self, name, value)

def _debug(*str):
    if 1:
        print str
