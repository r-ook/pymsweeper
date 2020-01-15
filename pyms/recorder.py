''' Record classes '''
import os
import pickle
import tkinter as tk

from .constants import RECORD

class RecordKeeper:
    default_filepath = os.path.split(os.path.abspath(__file__))[0]
    default_filename = os.path.join(default_filepath, 'guiness.pickle')

    def __init__(self, master, category_names, records_to_keep: int = 10):
        self.master = master
        if not self.load():
            self.categories = {name: [] for name in category_names}
        self.show()

    def show(self):
        ''' Build the main window contents '''
        # build the opt_cat menu
        self.window = tk.Toplevel(master=self.master, padx=5, pady=5)
        self.window.title('Highscores')
        self.window.focus_force()
        self.window.grab_set()
        self.var_cat = tk.StringVar()
        self.var_cat.trace('w', self._build_records)
        opt_cat = tk.OptionMenu(
            self.window,
            self.var_cat,
            *self.categories.keys(),
        )
        opt_cat.config(relief=tk.RIDGE)
        lbl_cat = tk.Label(master=self.window, text="Category: ")
        lbl_cat.grid(row=0, column=0)
        opt_cat.grid(row=0, column=1)

        # build the records frame
        self.frame = tk.Frame(master=self.window, padx=5, pady=5)
        self.frame.grid(row=1, column=0, columnspan=2)

        # set the default value - possibly use current mode to show.
        self.var_cat.set(next(iter(self.categories.keys())))
    
    def _build_records(self, *args):
        ''' Build the individual records '''
        for child in self.frame.winfo_children():
            child.destroy()
        
        record_entry = tk.Label(master=self.frame, text=self.var_cat.get() + ' some record')
        record_entry.pack()

    def save(self, filename=None):
        pass

    def load(self, filename=None):
        return None

# class Category:
#     def __init__(self, name: str, records_to_keep: int):
#         self.name = name

class RecordEntry:
    def __init__(self, data: RECORD):
        self.data = data
        self.diff_rate = self.data.amount / (self.data.x * self.data.y)

    @property
    def rating(self) -> float:
        '''
        Calculate the rating to apply against the duration
        Based on the numerous factors from blackjack mode
        On normal, always return 1.0 as there's no differentiating factors
        '''
        if self.data.mode_special:
            rate_guess = 1 - (self.data.guesses / self.data.amount)
            rate_hits = 1 - (self.data.hits / 21)
            rate_blew = 1 - (self.data.blew / 3 * (self.data.amount // 52 + 3))
            # the maximum possible blew amount are 9, 12, and 15 per 26, 52, and 104.
            mouseover = 1 - self.data.mouseover
            tracker = 1 - self.data.tracker
            hits_mode = (2 - self.data.allow_hits) / 2
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

def test():
    root = tk.Tk()
    def load():
        keeper = RecordKeeper(root, ['Normal1','Normal2','Normal3'])
    btn = tk.Button(root, text='highscores', command=load)
    btn.pack()
    root.mainloop()

if __name__ == '__main__':
    test()

