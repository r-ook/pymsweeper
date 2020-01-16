''' Record classes '''
import os
import pickle
import tkinter as tk
from random import randrange

from .constants import RECORD, MODES, MODE_CONFIG

class RecordKeeper:
    default_filepath = os.path.dirname(os.path.abspath(__file__))
    default_filename = os.path.join(default_filepath, '.guiness')

    @staticmethod
    def mode_str(mode:MODE_CONFIG):
        ''' Return the mode str '''
        return '{special}: {name} ({amount} IEDs @ {x}x{y})'.format(
            name=mode.name,
            special='Blackjack' if mode.special else 'Normal',
            amount=mode.amount,
            x=mode.x,
            y=mode.y
        )

    def __init__(self, master, records_to_keep: int = 10):
        self.master = master
        self._max = records_to_keep
        if not self.load():
            # TODO this needs to be changed later
            self.records = {RecordKeeper.mode_str(mode): [TestRecordEntry(val, RECORD(randrange(50), randrange(50), randrange(10), randrange(21), randrange(5), randrange(1), randrange(1), randrange(1), randrange(100))) for _ in range(self._max)] for val, mode in MODES.items()}
        self.record_vars = [RecordTkVar() for _ in range(self._max)]
        self.show()

    def show(self):
        ''' Build the main window contents '''
        # build the opt_cat menu
        window = tk.Toplevel(master=self.master, padx=5, pady=5)
        window.title('Highscores')
        window.focus_force()
        window.grab_set()
        self.var_mode = tk.StringVar()
        self.var_mode.trace('w', self._update_entries)
        opt_cat = tk.OptionMenu(
            window,
            self.var_mode,
            *self.records.keys(),
        )
        opt_cat.config(relief=tk.RIDGE)
        lbl_cat = tk.Label(master=window, text="Mode: ")
        lbl_cat.grid(row=0, column=0)
        opt_cat.grid(row=0, column=1)

        # build the records frame
        self.frm_main = tk.Frame(master=window, padx=5, pady=5)
        self.frm_main.grid(row=1, column=0, columnspan=2)
        self.build_records()

        # set the default value
        # TODO: Use current mode to show
        self.var_mode.set(next(iter(self.records.keys())))

    # def _build_header(self):
    #     frm = self.frm_main
    #     headers = ['Rank', 'Time', 'Seed', '']
    #     for text in headers:
    #         pass

    def add_record(self, mode_val, data):
        ''' Add record to mode '''
        records = self.records[RecordKeeper.mode_str(MODES.get(mode_val))]
        records.append(RecordEntry(mode_val, data))
        records.sort(key=lambda record: record.sort_key())
        records[:] = records[:self._max]

    def build_records(self):    # pylint: disable=unused-argument
        ''' Build the individual records '''
        # star argument to allow trace to use this callback
        # for child in self.frm_main.winfo_children():
        #     child.destroy()
        
        # for entry in self.records.get(self.var_mode.get()):
        #     # record_entry = tk.Label(master=self.frm_main, text=entry)        
        #     # record_entry.pack()
        #     self._build_entry(entry)
        frm = self.frm_main
        headers = ['Rank', 'Seed', 'Time', 
            '?', '!', '✨',
            '➕', '⚑', '♠',
            'Rating']
        for row in range(self._max):
            if row == 0:
                for i, header in enumerate(headers):
                    tk.Label(frm, text=header, padx=5).grid(row=row, column=i)
            else:
                for col in range(len(headers)):
                    if col == 0:
                        tk.Label(frm, text=row).grid(row=row, column=col)
                    else:
                        tk.Entry(frm, textvariable=self.record_vars[row-1][col-1], state='readonly', relief=tk.FLAT, width=5).grid(row=row, column=col)

    def _update_entries(self, *args):
        records = self.records.get(self.var_mode.get())
        for i, record in enumerate(records):
            self.record_vars[i].update(record)

    def _build_entry(self, entry):
        pass

    def save(self, filename=None):
        if not filename:
            filename = RecordKeeper.default_filename
        with open(filename, 'wb') as file:
            pickle.dump(self.records, file)

    def load(self, filename=None):
        _is_loaded = False
        if not filename:
            filename = RecordKeeper.default_filename
        try:
            with open(filename, 'rb') as file:
                self.records = pickle.load(file)
                _is_loaded = True
        except FileNotFoundError:
            print('File not found, assuming empty records...')
        except pickle.UnpicklingError:
            print('Pickle done goofed, need some troubleshooting...')
        except Exception as e:      # pylint: disable=broad-except
            # suppressing broad-except for now, will test to see what exceptions can be expected
            print('Not sure what went wrong, why not take a look:\n{e}'.format(e=e))
        return _is_loaded


class RecordEntry:
    def __init__(self, mode_val: int, data: RECORD):
        self.data = data
        self.mode = MODES.get(mode_val)
        # self.diff_rate = self.data.amount / (self.data.x * self.data.y)

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

class RecordTkVar:
    def __init__(self, n_data_to_show: int = 9):
        self.n = n_data_to_show
        self._vars = [tk.StringVar(value='test') for _ in range(self.n)]
    
    def update(self, record: RecordEntry):
        for i, var in enumerate(self._vars):
            if i < self.n:
                var.set(record.data[i])
            else:
                var.set(record.rating)
    
    def __getitem__(self, index):
        return self._vars[index]
        

class TestRecordEntry(RecordEntry):
    @property
    def rating(self):
        return .75


def test():
    root = tk.Tk()
    def load():
        keeper = RecordKeeper(root)
    btn = tk.Button(root, text='highscores', command=load)
    btn.pack()
    root.mainloop()

if __name__ == '__main__':
    test()

