from sqlite3 import *

conn = None

class DissociatedPress:
    def __init__(self,dbfilename):
        conn = connect(dbfilename)
