import os
import json

class Wal:
    def __init__(self, dir:str='data/wal'):
        self.dir = dir
        os.makedirs(self.dir, exist_ok=True)
        #recover last lsn from disk on startup
        self._current_lsn = self._load_last_lsn()

    def append(self, entry:dict):
        self._current_lsn += 1
        lsn = self._current_lsn
        wal_entry = {
            "lsn":lsn,
            "term":self._term,
            "type": entry["type"]
        }
