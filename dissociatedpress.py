# vim: encoding=utf-8

import sqlite3
import random


seed = None
"""Initial state (history) of the Markov chain"""

order = 5
"""Initial order of the Markov chain used to generate text"""

max_order = 10

_conn = None


def __init__(dbfilename="default.sqlite"):
    global _conn
    try:
        _conn = sqlite3.connect(dbfilename)
        cur=_conn.cursor()
        _conn.execute("select * from data")
        #cur.fetchone()
        #_debug(cur.fetchall())
        _conn.execute("select * from meta")
        #cur.fetchone()
        #_debug(cur.fetchall())
    except:
        _createDB()
    finally:
        _loadDB()

def _createDB():
    global max_order, _conn
    _conn.isolation_level="DEFERRED"
    _conn.execute("create table meta(name text, value text)")
    _conn.execute(
        """insert into meta(name, value) 
            values ('max_order',?)""",
        [max_order])
    sql = "create table data(text_id int default 0,"
    for i in range(max_order+1):
        sql += "c%i char" % i
        if i < max_order: sql += ","
    sql += ")"
    _conn.execute(sql)

def _loadDB():
    global max_order, _conn
    cur=_conn.cursor()
    cur.execute("select value from meta where name = 'max_order'")
    max_order=int(cur.fetchone()[0])

def _clearDB():
    global _conn
    _conn.execute("delete from data")

def analyze(input):
    global order, max_order, _conn
    _clearDB()
    if len(input)<max_order:
        raise Exception("input too short")

    input += input[:max_order]
        
    data = []
    for i in range(len(input)-max_order):
        str=input[i:i+max_order+1]
        data += [[c for c in str]]

    sql = "insert into data("
    for i in range(max_order+1):
        sql += "c%i" % i
        if i < max_order: sql += ","
    sql += ") values ("
    sql += "?,"*max_order + "?)"
    _conn.executemany(sql,data)
    _conn.commit()

def next(prefer=None):
    """Returns next character based on current chain settings"""

    global seed, order, max_order, _conn
    seed=seed[:order]

    sql = "select c%i from data where 1=1 " % order
    for i in range(order):
        sql +="and c%i=? " % i
    sql += "order by random() "
    cur = _conn.cursor()
    assert seed != None
    cur.execute(sql,[c for c in seed[:order]])
    _debug( "execute(%s,%s)", (sql,[c for c in seed[:order]]))
    row = cur.fetchone()
    if row == None:
        raise StopIteration("no next")
    nextchar = row[0]
    seed = seed[1:]+nextchar
    return nextchar

def _debug(*str):
    if 0:
        print str

__init__()
