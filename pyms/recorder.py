''' Record classes '''

# TODO - Check over the module to clear up any testing artifacts
import os
import pickle
import tkinter as tk

from tkinter.messagebox import askyesno, showerror
from .constants import RECORD, MODES, MODE_CONFIG

def get_mode(mode):
    ''' Convert to MODE_CONFIG if passed an int '''
    if isinstance(mode, int):
        mode = MODES.get(mode)
    return mode

class RecordKeeper:
    default_filepath = os.path.dirname(os.path.abspath(__file__))
    default_filename = os.path.join(default_filepath, '.data.pms')

    @staticmethod
    def mode_str(mode: MODE_CONFIG):
        ''' Return the mode str '''
        mode = get_mode(mode)
        return '{special}: {name} ({amount} IEDs @ {x}x{y})'.format(
            name=mode.name,
            special='Blackjack' if mode.special else 'Normal',
            amount=mode.amount,
            x=mode.x,
            y=mode.y
        )

    def __init__(self, parent, records_to_keep: int = 10):
        self.parent = parent
        self._max = records_to_keep
        self.is_loaded = False


    def init_records(self):
        ''' Initialize all records '''
        # Perhaps allow partially clearing by mode
        # If allow user to trigger, will need to import dialog.
        self.records = {RecordKeeper.mode_str(mode): [] for val, mode in MODES.items()}
        self.save()

    # The decorator needs to be static, so need to surpress the linter warning.
    # pylint: disable=no-self-argument
    def check_loaded(func):
        ''' A load checker decorator to handle file corruption issues '''

        def checking(self, *args, **kwargs):
            # First, check if file is loaded
            if not self.is_loaded:
                showerror('Corrupted Records', 'Unable to load/save highscore data until cleared.')
            else:
                func(self, *args, **kwargs)     # pylint: disable=not-callable
        return checking

    @check_loaded
    def show(self, current_mode=None):
        ''' Build the main window contents '''
        # build the opt_mode menu
        self.window = tk.Toplevel(master=self.parent, padx=5, pady=5)
        self.window.title('Highscores')
        self.window.focus_force()
        self.window.grab_set()
        self.var_records = [RecordTkVar() for _ in range(self._max)]
        self.var_mode = tk.StringVar(master=self.window)
        self.var_mode.trace('w', self._update_entries)
        opt_mode = tk.OptionMenu(
            self.window,
            self.var_mode,
            *self.records.keys(),
        )
        opt_mode.config(relief=tk.RIDGE)
        lbl_mode = tk.Label(master=self.window, text="Mode: ")
        self.window.grid_columnconfigure(index=0, weight=1)
        self.window.grid_columnconfigure(index=1, weight=2)
        lbl_mode.grid(row=0, column=0, sticky=tk.E)
        opt_mode.grid(row=0, column=1, sticky=tk.W)

        # build the records frame
        self.frm_main = tk.Frame(master=self.window, padx=5, pady=5)
        self.frm_main.grid(row=1, column=0, columnspan=2)
        self.build_records()
        btn_clear = tk.Button(master=self.window, text='CLEAR ALL RECORDS', command=self.clear_records)
        btn_clear.grid(row=2, column=0, columnspan=2)
        # self.__build_test_buttons()

        # set the default value
        if current_mode:
            self.var_mode.set(RecordKeeper.mode_str(current_mode))
        else:
            # fall back scenario - though, shouldn't reach this point unless testing.
            self.var_mode.set(next(iter(self.records.keys())))

    def __build_test_buttons(self):
        ''' buttons for testing '''
        btn_save = tk.Button(master=self.window, text='SAVE', command=self.save)
        btn_load = tk.Button(master=self.window, text='LOAD', command=self.load)
        btn_clear = tk.Button(master=self.window, text='CLEAR ALL RECORDS', command=self.clear_records)
        btn_save.grid(row=2, column=0)
        btn_load.grid(row=2, column=1)
        btn_clear.grid(row=2, column=2)

    def clear_records(self):
        proceed = askyesno('Clearing all records...',
                           'Are you sure you want to clear all records?\nThis CANNOT be undone.')
        if proceed:
            self.init_records()
        self.var_mode.set(self.var_mode.get())  # trigger call back to refresh

    @check_loaded
    def add_record(self, mode: MODE_CONFIG, data):
        ''' Add record to mode '''
        mode = get_mode(mode)
        records = self.records[RecordKeeper.mode_str(mode)]
        records.append(RecordEntry(mode, data))
        records.sort(key=lambda record: record.sort_key())
        records[:] = records[:self._max]
        self.save()

    def build_records(self):        # pylint: disable=unused-argument
        ''' Build the individual records '''
        frm = self.frm_main
        tk.Label(frm, text='♠ ⃞')   # ??? If I don't add this line, somehow the combining unicode headers will mess up...?!?!
        headers = ['Rank', 'Seed', 'Time',
                   '❓', '❗', '✨',
                   'Σ Hints', '⚑ Track', '♠ ⃞ Hits',
                   '♥ ⃞  Rating']
        stickys = [tk.W] + [tk.E] * 9
        justifys = [tk.LEFT] + [tk.RIGHT] * 9
        widths = [5, 10, 8] + [5] * 6 + [8]
        for row in range(self._max):
            if row == 0:
                for col, header in enumerate(headers):
                    tk.Label(frm, text=header, justify=justifys[col]).grid(row=row, column=col, sticky=stickys[col])
            else:
                for col in range(len(headers)):
                    if col == 0:
                        widget = tk.Label(frm, text=row)
                    else:
                        widget = tk.Entry(master=frm,
                                          textvariable=self.var_records[row-1][col-1],
                                          justify=justifys[col], state='readonly',
                                          relief=tk.FLAT, width=widths[col])
                    widget.grid(row=row, column=col, sticky=stickys[col])

    def _update_entries(self, *args):
        ''' Update the record variables with the current mode records '''
        records = self.records.get(self.var_mode.get(), [])
        records.sort(key=lambda record: record.sort_key())
        gen_records = iter(records)
        # records = iter(self.records.get(self.var_mode.get(), []))
        # for i, record in enumerate(records):
        #     self.var_records[i].update(record)
        for var in self.var_records:
            # r = next(records, None)
            # var.update(r)
            var.update(next(gen_records, None))

    def save(self, filename=None):
        if self.is_loaded:
            if not filename:
                filename = RecordKeeper.default_filename
            try:
                options = [opt.get() for opt in self.parent.options]
            except AttributeError:
                options = []
            with open(filename, 'wb') as file:
                pickle.dump((self.records, options), file)

    def load(self, filename=None):
        if not filename:
            filename = RecordKeeper.default_filename
        try:
            with open(filename, 'rb') as file:
                self.records, options = pickle.load(file)
                self.is_loaded = True
                return options

        except FileNotFoundError:
            print('File not found, assuming empty records...')
    
        except pickle.UnpicklingError:
            result = askyesno('Corrupted',
                'Records appear to be corrupted and cannot be loaded.\n\nClear ALL records and start fresh?')
            if not result:
                return None

        except Exception as e:      # pylint: disable=broad-except,invalid-name
            # suppressing pylint for now, will test to see what exceptions can be expected
            print('Not sure what went wrong, why not take a look:\n{e}'.format(e=e))
            return None

        # If no records are loaded for whatever reason, initiate the records unless stopped by users.
        if not self.is_loaded:
            self.init_records()
            self.is_loaded = True
        return None


class RecordEntry:
    '''
    RecordEntry class to manage additional functions from RECORD data
    
    Attributes:
    rating      - provide a rating derived from the RECORD data
    sort_key()  - provide a ranked index for sorting.
    '''    
    def __init__(self, mode: MODE_CONFIG, data: RECORD):
        self.data = data
        self.mode = get_mode(mode)

    @property
    def rating(self) -> float:
        '''
        Calculate the rating to apply against the duration
        Based on the numerous factors from blackjack mode
        On normal, always return 1.0 as there's no differentiating factors
        '''
        if self.mode.special:
            # Invert rate, i.e. the lower the initial values, the better the rating
            rate_guess = 1 - (self.data.IED_guesses / self.mode.amount)
            rate_hits = 1 - (self.data.IED_hits / 21)
            rate_blew = 1 - (self.data.IED_blew / 3 * (self.mode.amount // 52 + 3))
            # the maximum possible blew amount are 9, 12, and 15 per 26, 52, and 104.
            mouseover = 1 - self.data.opt_mouseover
            tracker = 1 - self.data.opt_tracker
            hits_mode = 1 - (self.data.opt_allow_hits / 2)

            # Calculate the weighted rating
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
            # Normal mode doesn't have any of these attributes to consider
            return 1.0

    def sort_key(self):
        ''' return the key for sorting '''
        # Increase time by rating, so that there is a penalty to a lower rating.
        key = 2 * self.data.time_val - self.data.time_val * self.rating
        return key

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'RecordEntry Object(time: {time_str}, rating: {rating}, data: {data})'.format(
            time_str=self.data.time_str,
            rating=self.rating,
            data=self.data
        )

class RecordTkVar:
    def __init__(self, n_data_to_show: int = 9):
        self.n = n_data_to_show
        self._default = ''
        self._vars = [tk.StringVar(value=self._default) for _ in range(self.n)]
        self.formatter = {
            'opt_mouseover': ['☐', '☒'],   #'☑'],
            'opt_tracker': ['☐', '☒'],     #'☑'],
            'opt_allow_hits': ['⛔', '☕', '♿'],
        }
    
    def update(self, record: RecordEntry = None):
        ''' Update the inner tkvars '''
        # print(type(record), RecordEntry, record.__class__, RecordEntry.__class__)
        if isinstance(record, RecordEntry):
            fields = record.data._fields
            for i, var in enumerate(self._vars):
                if i < 2:
                    # Seed and time
                    var.set(record.data[i+1])
                elif record.mode.special:
                    if i < self.n - 1:
                        if fields[i+1].startswith('opt'):
                            # use special format
                            var.set(self.formatter.get(fields[i+1])[record.data[i+1]])
                        else:
                            var.set(record.data[i+1])
                    else:
                        # if the last record, show rating instead
                        var.set('{:05.2f}%'.format(record.rating * 100))
                else:
                    var.set('-')
        else:
            self.clear()
    
    def clear(self):
        ''' Clear the inner tkvars '''
        for var in self._vars:
            var.set(self._default)

    @property
    def values(self):
        return [var.get() for var in self._vars]
    
    def __getitem__(self, index):
        return self._vars[index]

def _test():
    ''' Unit testing '''
    root = tk.Tk()
    def load():
        keeper = RecordKeeper(root)
        keeper.show()
    btn = tk.Button(root, text='highscores', command=load)
    btn.pack()
    root.mainloop()

if __name__ == '__main__':
    _test()
