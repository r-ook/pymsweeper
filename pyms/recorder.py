from . import constants as c
import os
import pickle

class RecordKeeper:
    default_filename = ''
    def __init__(self, category_names, records_to_keep:int=10):
        pass

    def save(self, filename=None):
        pass

    def load(self, filename=None):
        pass

class Category:
    pass

class Record:
    def __init__(self, time_elapsed, mode):
        # self.time_elapsed = time
        # self.mode = mode
        # self.x = x
        # self.y = y
        # self.IEDs = IEDs
        # self.hits = hits
        pass
    
    def rating(self):
        # rate = self.IEDs / (self.x * self.y)
        pass
    
    def clear_rate(self):
        pass
