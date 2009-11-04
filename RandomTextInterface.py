class RandomTextInterface(object):
    order = 4
    """Initial order of the Markov chain used to generate text"""

    max_order = 6

    seed = None
    """Initial state (history) of the Markov chain"""

    def loadDB(self, filepath="data.db"):
        """Loads sqlite3 database from the file at given path"""

    def next():
        """Returns next character based on current chain settings"""
