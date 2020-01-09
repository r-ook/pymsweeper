''' Record classes '''
from .constants import MODE_CONFIG, MODES
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
    def __init__(self, mode: MODE_CONFIG, time_elapsed, IEDs, hits=0, blew=0):
        self.mode = mode
        self.time_elapsed = time_elapsed
        self.IEDs = IEDs
        self.hits = hits
        self.blew = blew
    
    def rating(self):
        rate = self.mode.amount / (self.mode.x * self.mode.y)

    def normalize_amount(self):
        if self.mode.special:
            self.mode.amount
    
    def clear_rate(self):
        pass
