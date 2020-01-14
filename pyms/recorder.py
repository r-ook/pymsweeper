''' Record classes '''
import os
import pickle
import tkinter as tk

from .constants import RECORD

# def rate_calc(rater, total):
#     return (1 - (rater/total) * 100

class RecordKeeper:
    default_filename = ''
    def __init__(self, master, category_names, records_to_keep: int = 10):
        self.categories = [Category(name) for name in category_names]
        self.window = tk.Toplevel(master=master)
        self.window.title('Highscores')
        self.window.focus_force()
        self.window.grab_set()

    def save(self, filename=None):
        pass

    def load(self, filename=None):
        pass

class Category:
    def __init__(self, name):
        self.name = name

class Record:
    def __init__(self, data: RECORD):
        self.data = data
        self.mode = data.mode
        self.options = data.options
        self.diff_rate = self.mode.amount / (self.mode.x * self.mode.y)

    @property
    def rating(self) -> float:
        '''
        Calculate the rating to apply against the duration
        Based on the numerous factors from blackjack mode
        On normal, always return 1.0 as there's no differentiating factors
        '''
        if self.mode.special:
            rate_guess = 1 - (self.data.guesses / self.mode.amount)
            rate_hits = 1 - (self.data.hits / 21)
            rate_blew = 1 - (self.data.blew / 3 * (self.mode.amount // 52 + 3))
            # the maximum possible blew amount are 9, 12, and 15 per 26, 52, and 104.
            mouseover = 1 - self.options.mouseover.get()
            tracker = 1 - self.options.tracker.get()
            hits_mode = (2 - self.options.allow_hits.get()) / 2
            weighted_rates = [
                (rate_guess, .2),
                (rate_hits, .2),
                (rate_blew, .2),
                (mouseover, .05),
                (tracker, .05),
                (hits_mode, .3)
            ]
            return sum(r * w for r, w in weighted_rates)
        else:
            return 1.0

    def sort_key(self):
        ''' return the key for sorting '''
        # defined by time value x rating
        return self.data.time_val * self.rating

    def __str__(self):
        pass

    def __repr__(self):
        return 'Record Object(time: {time_str}, rating: {rating}, data: {data})'.format(
            time_str=self.data.time_str,
            rating=self.rating,
            data=self.data
        )
