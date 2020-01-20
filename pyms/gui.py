''' Main script that can also run as a module with -m '''
from . import constants as c
from . import recorder
from sys import maxsize
from time import time
from random import Random, randrange
from tkinter.messagebox import showinfo
from tkinter.simpledialog import askinteger

import tkinter as tk

class MyIntVar(tk.IntVar):
    ''' Subclassing the IntVar to add convenience methods '''
    def increase(self, num=1):
        self.change(num)

    def decrease(self, num=1):
        self.change(-num)

    def change(self, num):
        self.set(self.get() + num)

class GUI(tk.Tk):
    ''' Main tkinter class that hosts window configs '''
    # pylint: disable=too-many-instance-attributes
    # Suppressing the pylint warning as there are a bunch of frames to consider
    # and would be easier accessed by name instead of dict

    def __init__(self):
        super().__init__()
        self.title('Pysweeper')

        # generic image to force compound sizing on widgets
        self.empty_image = tk.PhotoImage(width=1, height=1)

        # Create record instance and load records and options
        self.record_keeper = recorder.RecordKeeper(self)

        opt_val = self.record_keeper.load()
        if not opt_val:
            # set default values if nothing to load
            opt_val = [3, 0, 1, 1, 1]
    
        # Set up tk variables and create menus and timer
        # self.options.mode = tk.IntVar(value=3)
        self.options = c.OPTIONS(
            tk.IntVar(name='Mode'),
            *(tk.BooleanVar(name=opt_name) for opt_name in ('Warning Sound', 'Σ Mouseover Hint', '⚑ Flags Tracker')),
            tk.IntVar(name='Hits Option')
        )
        for _idx, _opt in enumerate(self.options):
            _opt.set(opt_val[_idx])
            _opt.trace('w', lambda *_, idx=_idx: self.option_callback(idx))
        self.create_menus()
        self.wm_protocol('WM_DELETE_WINDOW', self.exit)
        self.taco_bell(self.options.sound.get())
        self.timer = Timer(self)
        self.field = None

        # Set up a blank label for default fg and bg global, to be more OS friendly
        _lbl = tk.Label(self, text='')
        global DEFAULT_FG
        global DEFAULT_BG
        DEFAULT_FG = _lbl.cget('fg')
        DEFAULT_BG = _lbl.cget('bg')
        _lbl.destroy()
        del _lbl

        # Set up the frames
        self.frm_main = tk.Frame(self)
        self.frm_helper = tk.Frame(self)
        self.hinter = HintBar(self, self.frm_helper)
        self.clueshelper = NumbHelper(self, self.frm_helper)

        # Build the main frames
        self.build_status_bar()
        self.frm_main.grid(row=1, column=0, sticky=tk.NSEW)
        self.frm_helper.grid(row=2, column=0, sticky=tk.NSEW)
        self.frm_helper.grid_columnconfigure(index=0, weight=1)
        self.frm_helper.bind('<Expose>', GUI.widget_exposed)
        self.hinter.build()
        self.build_field(c.MODES.get(self.options.mode.get()))

    def taco_bell(self, state):
        ''' Toggle bell '''
        self.bell = super().bell if state else lambda: None

    def check_allow_hits(self, state):
        ''' Toggle hits if using numbered mode '''
        if state > 0 and self.options.mode.get() >= 3:
            self.frm_IEDs.grid_configure(columnspan=1)
            self.frm_blew.grid()
        else:
            self.frm_IEDs.grid_configure(columnspan=2)
            self.frm_blew.grid_remove()
        # Change the current threshold if field exists, bypassing if field isn't created yet
        try:
            self.field.allow_threshold(state)
        except AttributeError:
            # field doesn't exist yet
            pass

    def option_callback(self, opt_index: int):
        ''' Callback option to call functions based on tkVar triggered '''
        # Using id(...) to overcome the unhashable tk Vars
        # parser = {
        #     id(self.options.sound): self.taco_bell,
        #     id(self.options.mouseover): self.hinter.show,
        #     id(self.options.tracker): self.clueshelper.show,
        #     id(self.options.allow_hits): self.check_allow_hits,
        # }
        opt_value = self.options[opt_index].get()
        parser = [
            self.build_field,
            self.taco_bell,
            self.hinter.show,
            self.clueshelper.show,
            self.check_allow_hits
        ]
        try:
            self.field._cached_options[opt_index] = max(self.field._cached_options[opt_index], opt_value)
        except AttributeError:
            # _cached_options does not exist yet
            pass
        parser[opt_index](opt_value)

    @staticmethod
    def widget_exposed(evt):
        ''' Hide helper frame if all the hinters are disabled '''
        if not any(child.winfo_viewable() for child in evt.widget.children.values()):
            evt.widget.config(height=1)

    def create_menus(self):
        ''' Menu setups '''
        # Creating menus...
        menubar = tk.Menu(self)
        norm_modes = tk.Menu(self, tearoff=0)
        numb_modes = tk.Menu(self, tearoff=0)

        # Setting the modes...
        for idx, mode in c.MODES.items():
            mode_menu = numb_modes if mode.special else norm_modes
            mode_menu.add_radiobutton(
                label=mode.name,
                value=idx,
                variable=self.options.mode
                # command=lambda build_mode=mode: self.build_field(build_mode)
            )

        # Adding difficulty menu...
        diff_menu = tk.Menu(self, tearoff=0)
        diff_menu.add_cascade(label='☺ Normal', menu=norm_modes)
        # diff_menu.add_cascade(label='♠ Blackjack', menu=numb_modes)
        diff_menu.add_cascade(label='♠ ⃞ Blackjack', menu=numb_modes)

        # Adding option menu...
        self.options_menu = tk.Menu(self, tearoff=0)
        self.special_menu = tk.Menu(self, tearoff=0)
        hits_menu = tk.Menu(self.special_menu, tearoff=0)

        o = self.options
        self.options_menu.add_command(label='Use seed...', command=self.ask_for_seed)
        self.options_menu.add_checkbutton(label=o.sound._name, variable=o.sound)            #pylint: disable=protected-access
        self.special_menu.add_checkbutton(label=o.mouseover._name, variable=o.mouseover)    #pylint: disable=protected-access
        self.special_menu.add_checkbutton(label=o.tracker._name, variable=o.tracker)        #pylint: disable=protected-access
        hits_menu.add_radiobutton(label='⛔ Disallow Hits', value=0, variable=o.allow_hits)
        hits_menu.add_radiobutton(label='☕ Allow Hits on guesses only', value=1, variable=o.allow_hits)
        hits_menu.add_radiobutton(label='♿ Allow Hits on any clicks', value=2, variable=o.allow_hits)        
        # for opt in options:
        #     self.special_menu.add_checkbutton(label=opt._name, variable=opt)    #pylint: disable=protected-access
        self.special_menu.add_cascade(label='☄ Hits', menu=hits_menu)
        self.options_menu.add_cascade(label='♠ ⃞ Blackjack', menu=self.special_menu)

        # Compile the menus together...
        menubar.add_cascade(label='Modes', menu=diff_menu)
        menubar.add_cascade(label='Options', menu=self.options_menu)
        menubar.add_command(label='Highscores', command=lambda x=self.options.mode: self.record_keeper.show(x.get()))
        self.config(menu=menubar)

    def ask_for_seed(self):
        seed = askinteger(
            'Generate from seed',
            'Please enter the seed number you wish to use.\n\nNote: Highscores will NOT be recorded!',
            minvalue=0,
            maxvalue=maxsize,
            parent=self
        )
        self.build_field(mode=self.options.mode.get(), seed=seed)

    def build_status_bar(self):
        ''' Build the timer, big button and counter '''
        # Create all the widgets and frames...
        self.frm_status = tk.Frame(self)
        self.frm_timer = tk.LabelFrame(self.frm_status, text='Time:')
        self.lbl_timer = tk.Label(self.frm_timer, textvariable=self.timer.string)
        self.btn_main = tk.Button(
            self.frm_status,
            image=self.empty_image,
            command=lambda: self.build_field(c.MODES.get(self.options.mode.get())),
            # font=('tkDefaultFont', 18, 'bold'),
            width=32,
            height=32,
            compound='c',
            relief=tk.GROOVE
        )
        self.update_status(c.STATUS_OKAY)
        self.frm_IEDs = tk.LabelFrame(self.frm_status, text='IEDs:')
        self.lbl_IEDs = tk.Label(self.frm_IEDs, text='0')
        self.frm_blew = tk.LabelFrame(self.frm_status, text='Hits:')
        self.lbl_blew = tk.Label(self.frm_blew, text='0')

        # Grid management for tk... ugh
        self.frm_status.grid(row=0, column=0, sticky=tk.NSEW)
        for idx, weight in enumerate((6, 2, 3, 3)):
            self.frm_status.columnconfigure(index=idx, weight=weight)
        self.frm_timer.grid(row=0, column=0, sticky=tk.NSEW)
        self.btn_main.grid(row=0, column=1, sticky=tk.NS)
        self.frm_IEDs.grid(row=0, column=2, sticky=tk.NSEW)
        self.frm_blew.grid(row=0, column=3, sticky=tk.NSEW)
        self.lbl_timer.pack()
        self.lbl_IEDs.pack()
        self.lbl_blew.pack()

    def build_field(self, mode: c.MODE_CONFIG, seed=None):
        ''' Build the field frame, stop the timer and update the counters '''
        # Quick check if int is provided, convert to MODE_CONFIG.
        if isinstance(mode, int):
            mode = c.MODES.get(mode)

        # See if possible to seperate the special mode later....
        if mode.special:
            self.clueshelper.build(mode.amount // 13)
            self.options_menu.entryconfig('♠ ⃞ Blackjack', state=tk.NORMAL)
            for opt_index in range(2, 4):       # mouseover and tracker
                self.option_callback(opt_index)
        else:
            self.options_menu.entryconfig('♠ ⃞ Blackjack', state=tk.DISABLED)
            if self.hinter.exists:
                self.hinter.show(False)
            if self.clueshelper.exists:
                self.clueshelper.destroy()

        # See if allow_hit frame needs to be hidden or shown
        self.check_allow_hits(self.options.allow_hits.get())

        # Actually starting the field
        if not self.field is None:
            self.field.destroy()
        self.field = Field(self, mode, seed=seed)
        self.field.build()
        self.lbl_IEDs.config(textvariable=self.field.IED_current)
        self.lbl_blew.config(textvariable=self.field.IED_hit)
        self.update_status(c.STATUS_OKAY)
        self.timer.reset()

    def update_status(self, status:c.STATUS):
        ''' Update main happy face button '''
        self.btn_main.config(
            text=status.icon,
            fg=status.fg,
            bg=status.bg,
            font=status.font
        )

    def exit(self, save=True):
        if save: self.record_keeper.save()
        self.destroy()
        self.quit()

    def run(self):
        self.mainloop()        

class Timer:
    '''
    Timer object to manage... the timer... 
    Most of the methods are rather self explanatory
    '''
    def __init__(self, parent):
        self.parent = parent
        self.string = tk.StringVar()
        self._job = None
        self.start_time = 0
        self.end_time = 0
        self.active = False
        self.reset()

    def stop_update(self):
        self.active = False
        if self._job is not None:
            self.parent.after_cancel(self._job)
            self._job = None

    def reset(self):
        self.stop_update()
        self.string.set('00:00:00')
        self.start_time = 0
        self.end_time = 0

    def start(self):
        self.start_time = time()
        self.active = True
        self._update()

    def _update(self):
        if self.active:
            self.to_string()
            self._job = self.parent.after(ms=1000, func=self._update)

    def to_string(self):
        ''' Format and set the string variable to the time '''
        current = time() - self.start_time
        h, m, s = int(current // 3600), int(current % 3600 // 60), int(current % 60)
        self.string.set('{h:02}:{m:02}:{s:02}'.format(h=h, m=m, s=s))

    def stop(self):
        self.end_time = time() - self.start_time
        self.to_string()
        self.stop_update()


class Field:
    ''' The field that contains all the Map elements and handle the events '''
    # pylint: disable=too-many-instance-attributes
    # Suppress pylint warning for now
    # Want to see if some attributes can be handled as classes

    def __init__(self, parent: GUI, mode: c.MODE_CONFIG = c.MODES.get(0), seed: int = None):
        self.parent = parent
        self.mode = mode
        self.frame = tk.Frame(master=self.parent.frm_main)
        self.is_over = False
        self.seed = seed
        self._used_seed = seed is not None

        # The original intent was to use rate to determine amount,
        # left here as a legacy, might be revisited
        if self.mode.amount:
            self.IED_count = self.mode.amount
        else:
            self.IED_count = int(self.mode.x * self.mode.y * self.mode.rate)
        self.IED_current = MyIntVar(value=self.IED_count)
        self.IED_guessed = 0
        self.IEDs = set()
        self._IEDs_are_set = False
        self.map_cleared = 0
        self.map = {
            (x, y): NumbedMapElem(self, (x, y)) if self.mode.special else MapElem(self, (x, y)) 
            for x in range(self.mode.x)
            for y in range(self.mode.y)
        }
        if mode.special:
            self.allow_threshold(self.parent.options.allow_hits.get())
        else:
            self.IED_threshold = 0
        self.IED_hit = MyIntVar(value=0)
        self.IED_blew = 0
        self.map_goal = self.mode.x * self.mode.y - self.IED_count

    def allow_threshold(self, state=0):
        ''' Enable or disable hits threshold '''
        self.IED_threshold = 21 if state > 0 else 0

    def build(self):
        ''' Build the frame and map elements '''
        for elem in self.map.values():
            elem.build_surprise_box()
        self.frame.pack_propagate(False)
        self.frame.pack()

    def set_IEDs(self, current_coord: tuple = None):
        ''' Initial planting of IEDs on first click '''
        # check if set_IEDs has already been called
        if not self._IEDs_are_set:
            # check if seed was provided, if not, generate a new seed
            if self.seed is None:
                self.seed = randrange(maxsize)
            rnd = Random(self.seed)
            # Randomize coord and add set if it's not the current location
            while len(self.IEDs) < self.IED_count:
                coord = (rnd.randrange(self.mode.x), rnd.randrange(self.mode.y))
                if coord != current_coord or self._used_seed:
                    self.IEDs.add(coord)

            # Use card values if Blackjack mode, else IEDs are assigned default value of 1 (True)
            if self.mode.special:
                cards = list(range(1, 10)) + [10] * 4
                cards = cards * (self.mode.amount // 13)
                rnd.shuffle(cards)
                for IED in sorted(self.IEDs):
                    self.map.get(IED).is_IED = cards.pop()
            else:
                for IED in sorted(self.IEDs):
                    self.map.get(IED).is_IED = 1

            self._IEDs_are_set = True
            self._cached_options = [opt.get() for opt in self.parent.options]
            # Start the timer once everything is set up
            self.parent.timer.start()

    def expose_IEDs(self, clear, show_false_flags=False):
        ''' Reveal unflagged IEDs and false flags when over '''
        for IED in self.IEDs:
            self.map[IED].reveal(over_and_clear=clear)
        if show_false_flags:
            for elem in self.map.values():
                if elem.flagged:
                    elem.check_false_flag()

    def check_threshold(self, elem, guessed=False, guess_safe=None):
        ''' Check if threshold is exceeded '''
        # Added guessed argument to support mid-click guesses
        if guessed:
            self.IED_guessed += 1
        else:
            self.IED_current.decrease()
        if not guess_safe:
            self.IED_hit.increase(elem.is_IED)
            self.IED_blew += 1
        current_hit = self.IED_hit.get()
        if current_hit > self.IED_threshold or (self.parent.options.allow_hits.get() < 2 and not guessed):
            self.bewm(elem)
        elif current_hit >= 17:
            self.parent.update_status(c.STATUS_WOAH)

    def bewm(self, last):
        ''' When the field blows up '''
        self.parent.timer.stop()
        last.is_final()
        self.parent.update_status(c.STATUS_BOOM)
        self.is_over = True
        self.expose_IEDs(clear=False, show_false_flags=True)

    def check_clear(self):
        ''' Check for when the field is cleared '''
        self.map_cleared += 1
        if self.map_cleared >= self.map_goal:
            self.parent.timer.stop()
            self.is_over = True
            self.parent.update_status(c.STATUS_YEAH)
            self.expose_IEDs(clear=True)
            congrats = 'You did it!'
            if self.IED_threshold > 0:
                congrats += ' You took {n} guess{plural}.'.format(n=self.IED_guessed, plural='es' if self.IED_guessed > 1 else '')
                hit = self.IED_hit.get()
                if hit:
                    congrats += '\n... But you hit {hit} point{plural}.\nAim for 0 next time!'.format(hit=hit, plural="s" if hit > 1 else "")
                else:
                    congrats += '\nAnd you managed to remain clear without hitting any mines.\nCongrats!'
            if self._used_seed:
                congrats += '\n\n(Highscore not added as seed has been used)'
            else:
                self.parent.record_keeper.add_record(
                    self.mode,
                    c.RECORD(
                        self.parent.timer.end_time,
                        self.seed,
                        self.parent.timer.string.get(),
                        *(
                            (
                                self.IED_guessed,
                                self.IED_hit.get(),
                                self.IED_blew,
                                *self._cached_options[-3:]
                            ) if self.mode.special else (0, ) * 6
                        )
                    )
                )
            showinfo('Awesome!', congrats)

    def destroy(self):
        self.frame.destroy()

def gradient_colour(main:int, increm=0x080808, n=8, darken=True, as_string=False) -> list:
    '''
    Create a set of gradient colours based on the proided main colour, returns a list.

    main        = starting RGB value
    increm      = value to change the gradient shades by (default: 0x080808)
    n           = number of total colours to return (default: 8)
    darken      = if True, colours will decrease in value (darken), if False, the other direction (default: True)
    as_string   = if True, returns as RBG string value "#FFFFFF", else, in integer  (default: False)
    '''
    if isinstance(main, str):
        try:
            main = int(main, 16)
        except ValueError:
            return []
    if as_string:
        colours = ['#{:06x}'.format(main + (-i if darken else i) * increm) for i in range(n)]
    else:
        colours = [main + (-i if darken else i) * increm for i in range(n)]
    return colours

def zip_gradient(colours: list, **kwargs):
    '''
    Using gradient colour method, return a list of the gradient tuples transposed by the original list
    i.e. if a list of [a, b, c] was provided, returns:
    [
        (a1, b1, c1),
        (a2, b2, c2),
        (a3, b3, c3),
        ...
    ]
    '''
    kwargs = {kw: val for kw, val in kwargs.items() if kw in ('increm', 'n', 'darken', 'as_string')}
    grads = [gradient_colour(c, **kwargs) for c in colours]
    return list(zip(*grads))

class MapElem:
    ''' Map element base class to handle individual cells '''

    # Colours associated with clue numbers
    clue_colours = {
        1: 'blue',
        2: 'forest green',
        3: 'red2',
        4: 'navy',
        5: 'maroon',
        6: 'cyan4',
        7: 'purple',
        8: 'seashell4',
        9: 'goldenrod',
        10: 'pink4'
    }
    def __init__(self, field: Field, coord):
        self.field = field
        self.coord = coord
        self.frame = tk.Frame(self.field.frame, width=24, height=24)
        self.frame.pack_propagate(False)
        self.is_IED = 0
        self.clue = 0
        self._flagged = 0
        self.revealed = False
        self.clueshelper = self.field.parent.clueshelper
        self.box = None
        self.lbl = None
        self._adjacents = None

    @property
    def flagged(self):
        ''' Returns whether the cell is flagged '''
        return self._flagged

    @flagged.setter
    def flagged(self, num):
        ''' Flag cells and manage clue tracker, and IED count '''
        # slightly ugly way to standardize the flag handling below instead of a bunch of if/else statements.
        for i, check in enumerate((self._flagged, num)):
            i = i * 2 - 1   
            # so that 0 = -1, 1 = 1; i.e. num=0 will decrease flag and IED, num=1 will increase.
            if check != 0:
                self.clueshelper.change_flag(check, i)
            elif not self.revealed:
                self.field.IED_current.change(i)
        self._flagged = num

    def get_flag_config(self, num=None):
        ''' Config how the flag should display '''
        # pylint: disable=unused-argument
        # The num argument is there to be consistent with the child class that relies on the same flag method.
        # Eventually will want to restructure this properly
        return {'text': '⚑'}

    def flag(self, num=None):
        ''' Handles updating of the concealer box visual '''
        if num is None:
            num = 1
        if self.flagged == num:
            self.box.config(text=' ')
            self.flagged = 0
        else:
            self.box.config(**self.get_flag_config(num))
            self.flagged = num

    def check_false_flag(self):
        ''' Check if box is false flagged '''
        if not self.is_IED:
            self.box.config(**self.get_false_guess_config())

    def get_false_guess_config(self):
        ''' config for false flag checker '''
        return {'text': '❌', 'fg': 'white', 'bg': 'maroon'}

    def build_surprise_box(self):
        ''' Build the concealer button '''
        self.box = Surprise(self)
        self.frame.grid(row=self.coord[1], column=self.coord[0], sticky=tk.NSEW)
        self.box.pack()
        return self.box

    @property
    def adjacents(self):
        ''' Set or initialize adjacent cell references '''
        if self._adjacents is None:
            cx, cy = self.coord
            mapper = self.field.map
            self._adjacents = [mapper.get((rx, ry)) for rx in range(cx-1, cx+2) for ry in range(cy-1, cy+2) if mapper.get((rx, ry))]
            self._adjacents.remove(self)
        return self._adjacents

    def adjacent_IEDs(self):
        ''' Find adjacent IED totals '''
        return 0 if self.is_IED else sum(adj.is_IED for adj in self.adjacents)

    def adjacent_flags(self):
        ''' Find adjacent Flag totals '''
        return sum(adj.flagged + (adj.is_IED * int(adj.revealed)) for adj in self.adjacents)

    def get_IED_config(self, final=False):
        ''' Provide the config of how the IED is represented '''
        config = {
            True: {'text': '✨', 'fg': 'red'},
            False: {'text' : '☀'}
        }.get(final)
        config.update({'font' : ('tkDefaultFont', 12, 'bold')})
        return config

    def is_final(self):
        ''' The last elem config before the field is blown '''
        if self.is_IED:
            self.lbl.config(**self.get_IED_config(final=True))
        else:
            self.lbl.config(**self.get_false_guess_config())
            if self.clue:
                self.lbl.config(text=self.clue)

    def label_actual(self):
        ''' Set up the underlayer label '''
        # This is separated so it's easier to manage the subclass
        if self.is_IED:
            actual = self.get_IED_config()
        else:
            actual = {
                'text' : self.clue if self.clue else '',
                'fg' : self.__class__.clue_colours.get(self.clue, DEFAULT_FG),
                'font' : ('tkDefaultFont', 10, 'bold'),
            }

        lbl = tk.Label(master=self.frame, **actual)
        return lbl

    def create_actual(self):
        ''' Create the underlayer label '''
        self.lbl = self.label_actual()
        if self.is_IED == 0:
            self.lbl.bind('<ButtonRelease-1>', self.omni_click)
            self.lbl.bind('<ButtonRelease-3>', self.omni_click)
        self.lbl.pack(fill=tk.BOTH, expand=True)

    def clicked(self, guess_safe=None):
        ''' Concealer box was clicked '''
        go_ahead = self.reveal(guess_safe=guess_safe)
        if go_ahead:
            # Open adjacent cells if current is empty
            if self.clue == 0 and not self.is_IED:
                for adj in self.adjacents:
                    adj.clicked()

            # Unless it's confirmed guess_safe (flag = IED), do the checks.
            # if not guess_safe:
            if self.is_IED:
                self.field.check_threshold(self, guessed=guess_safe is not None, guess_safe=guess_safe)
            elif guess_safe is False: # and is not IED
                self.field.bewm(self)
            else:
                self.field.check_clear()

    def reveal(self, guess_safe=None, over_and_clear=None):
        ''' Reveal the block if not already revealed '''
        # This go_ahead is needed to stop the recursion of adjacent clicking from happening
        # It removes the need to do the same check twice in both methods
        go_ahead = (not self.revealed and (self.flagged == 0 or guess_safe is not None))
        if go_ahead:
            if self.field.map_cleared == 0:
                self.field.set_IEDs(self.coord)
            self.revealed = True
            if self.flagged:
                self.flagged = 0
            self.clue = self.adjacent_IEDs()
            self.create_actual()
            self.box.pack_forget()
            # Check if it's guess_safe and in a winning condition to highlight mines
            if guess_safe or over_and_clear:
                self.lbl.config(bg='lightblue')

            # If the game is over, skip updating the hinter.
            if self.is_IED and over_and_clear is None:
                self.clueshelper.guessed_flag(self.is_IED, guess_safe=guess_safe)

        # pass the condition back to self.clicked
        return go_ahead

    def omni_click(self, evt, ignore=False):
        ''' Main handler for clicking, branches off to sub methods... '''
        if not self.field.is_over:
            # Make sure the cursor is within the same block, allow users to change their mind.
            w, h = evt.widget.winfo_geometry().replace('+', 'x').split('x')[:2]
            if evt.x in range(int(w)) and evt.y in range(int(h)):
                # Both buttons are pressed
                if (evt.num == 1 and evt.state & c.MOUSE_RIGHT) or (evt.num == 3 and evt.state & c.MOUSE_LEFT):
                    self.both_release()
                elif evt.num == 1:
                    self.left_release()
                # Mid click for special mode
                elif evt.num == 2:
                    if self.flagged:
                        self.clicked(guess_safe=self.flagged == self.is_IED)
                elif evt.num == 3 and not ignore:
                    self.right_release()

    def left_release(self):
        ''' Remove the concealer '''
        self.clicked()

    def right_release(self):
        ''' Flag the concealer '''
        ### still trying to figure out if right release can be separated from right click for fast flagging
        # unheld = (evt.state & c.MOUSE_LEFT > 0) if evt else True
        # if not self.revealed and unheld:
        if not self.revealed:
            self.flag()

    def both_release(self):
        ''' Open adjacent blocks '''
        if self.adjacent_flags() == self.clue and self.revealed:
            self.clicked()
            for adj in self.adjacents:
                adj.clicked()
        else:
            self.field.parent.bell()

class NumbedMapElem(MapElem):
    ''' Subclassed Numbered Map element for Blackjack mode '''
    # use original Clue colours for IED colours
    val_colours = MapElem.clue_colours
    # set new gradient for new clue colours as they can get up to 80 now.
    clue_colours = {
        i: clue_colour for i, clue_colour in enumerate(
            colour for c_set in zip_gradient(
                [
                    0x804868,
                    0x5858C0,
                    0x58C058,
                    0xC05858,
                    0x58C0C0,
                    0xC0C058,
                    0xC058C0,
                    0xA06048,
                    0x6048A0,
                    0x48A060
                ],
                as_string=True
            ) for colour in c_set
        )
    }

    def right_release(self):
        ''' overriden right_release to cycle through 0 - 10 with each click '''
        if not self.revealed:
            self.flag((self.flagged + 1) % 11)

    def get_IED_config(self, final=False):
        config = {
            'text' : c.NEG_CIRCLED_NUMBERS.get(self.is_IED),
            'fg' : NumbedMapElem.val_colours.get(self.is_IED),
            'font' : ('tkDefaultFont', 12)
        }
        if not self.field.is_over:
            config.update(
                {
                    'bg': 'gold', # 'maroon'
                    'relief': tk.SUNKEN
                }
            )
        if final:
            config.update({'fg': 'white', 'bg': 'red3'})
        return config

    def get_flag_config(self, num=None):
        return {
            'text': c.CIRCLED_NUMBERS.get(num, ' '),
            'fg': NumbedMapElem.val_colours.get(num),
            'font': ('tkDefaultFont', 12)
        }

    def create_actual(self):
        super().create_actual()
        if self.is_IED == 0:
            self.lbl.bind('<Enter>', lambda e: self.field.parent.hinter.update(self))
            self.lbl.bind('<Leave>', self.field.parent.hinter.reset)

    def build_surprise_box(self):
        self.box = NumbedSurprise(self)
        self.frame.grid(row=self.coord[1], column=self.coord[0], sticky=tk.NSEW)
        self.box.pack()
        return self.box

    def check_false_flag(self):
        if self.flagged != self.is_IED:
            self.box.config(**self.get_IED_config())
            self.box.config(bg='orange')
        super().check_false_flag()


class Surprise(tk.Button):
    ''' Concealer button object to handle bindings '''

    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        super().__init__(
            master=self.parent.frame,
            text=' ',
            fg='orange red',
            image=self.parent.field.parent.empty_image,
            width=20, height=20,
            compound='c',
            relief=tk.GROOVE,
            *args, **kwargs
        )
        self.flag = self.parent.flag

        self.bind('<ButtonRelease-1>', self.parent.omni_click)
        self.bind('<ButtonRelease-3>', self.parent.omni_click)
        self.bind('<Enter>', lambda e: self.focus_set())
        self.bind('<Leave>', lambda e: self.parent.frame.focus_set())
        self.set_other_bindings()
    
    def set_other_bindings(self):
        self.bind('1', lambda evt: self.flag(None))
        # self.bind('<Button-3>', parent.omni_click)


class NumbedSurprise(Surprise):
    ''' Subclass concealer button to handle additional flagging '''

    def set_other_bindings(self):
        self.bind('<ButtonRelease-2>', self.parent.omni_click)

        # NUM binding
        for i, s in enumerate('1234567890', 1):
            if i > 10: i = 10
            self.bind(s, lambda e, x=i: self.flag(x))

        # WASD binding
        for i, s in enumerate('qweasdzxc', 4):
            if i > 10: i = 10
            self.bind(s, lambda e, x=i: self.flag(x))
            self.bind(s.upper(), lambda e, x=i: self.flag(x))

class HintBar:
    ''' Hint bar to help users calculate remaining flags '''

    def __init__(self, gui: GUI, parent_frame):
        self.gui = gui
        self.frame = None
        self.parent_frame = parent_frame
        self.hints = None
        self.exists = False    

    def build(self):
        ''' build the HintBar frame '''
        if self.exists:
            self.destroy()
        self.frame = tk.Frame(master=self.parent_frame)
        self.hints = {
            k: self.create_inner_frame(k)
            for k in ('Total', 'Flags/Hits', 'Remaining')
        }
        for i, hint in enumerate(self.hints.values()):
            hint.frame.grid(row=0, column=i, sticky=tk.NSEW)
            hint.label.pack(fill=tk.BOTH, expand=True)
        for i in range(3):
            self.frame.columnconfigure(index=i, weight=1)
        self.exists = True

    def show(self, state):
        ''' Toggler to show or hide the frame '''
        if state:
            self.frame.grid(row=0, column=0, sticky=tk.NSEW)
        else:
            self.frame.grid_remove()

    def create_inner_frame(self, ctype):
        def validate(hinter):
            if hinter.counter.get() < 0:
                hinter.label.config(bg='yellow')
            else:
                hinter.label.config(bg=DEFAULT_BG)
        frame = tk.LabelFrame(master=self.frame, text='{}:'.format(ctype))
        counter = tk.IntVar()
        label = tk.Label(master=frame, textvariable=counter)
        hinter = c.HINT(frame, label, counter)
        counter.trace('w', lambda *args: validate(hinter))
        return hinter

    def update(self, hinter: NumbedMapElem):
        if not self.gui.field.is_over:
            total = hinter.clue
            flags_hits = hinter.adjacent_flags()
            remaining = total - flags_hits
            self.hints['Total'].counter.set(total)
            self.hints['Flags/Hits'].counter.set(flags_hits)
            self.hints['Remaining'].counter.set(remaining)

    def reset(self, *args):
        ''' Reset hintbar to zeroes '''
        #pylint: disable=unused-argument
        # The star arugment is to bypass the binding events.
        if not self.gui.field.is_over:
            for hint in self.hints.values():
                hint.counter.set(0)

    def destroy(self):
        self.exists = False
        self.frame.destroy()

class NumbTracker:
    def __init__(self, maximum):
        self.maximum = maximum
        self.blew_count = 0
        self.lock_count = 0
        self.flag_count = 0

    @property
    def total(self):
        return sum((self.flag_count, self.blew_count, self.lock_count))

    @property
    def over(self):
        return self.total > self.maximum

    def change(self, change=1):
        self.flag_count = max(0, self.flag_count + change)

    def blew(self):
        self.blew_count += 1

    def lock(self):
        self.lock_count += 1

class NumbHelper(tk.Frame):
    ''' Helper Frame object to help track flags '''
    FLAG_ACTIVE = 'forestgreen'
    FLAG_LOCK = 'dodger blue'
    FLAG_BLEW = 'red2'
    FLAG_OVER = 'gold'
    # FLAG_OKAY = DEFAULT
    FLAG_INACTIVE = 'LightCyan3'
    def __init__(self, parent, parent_frame):
        self.parent = parent
        self.parent_frame = parent_frame
        self.nrows = None
        self.trackers = None
        self.exists = False
        self.tracker_configs = {
            1: c.TRACKER_CONFIG(1, NumbHelper.FLAG_OVER, 0, NumbHelper.FLAG_ACTIVE),
            -1: c.TRACKER_CONFIG(0, DEFAULT_BG, 1, NumbHelper.FLAG_INACTIVE)
        }

    def build(self, nrows):
        if self.exists:
            self.destroy()
        self.nrows = nrows
        self.trackers = {
            i: NumbTracker(self.nrows * (4 if i >= 10 else 1))
            for i in range(1, 11)
        }
        super().__init__(master=self.parent_frame)
        self.create_labels()
        self.exists = True

    def show(self, state=True):        
        self.grid(row=1, column=0) if state else self.grid_remove()

    def create_labels(self):
        self.lbls = {
            # tuple key set up as (number, count=1, 2, 3, 4...)
            (num, count + 1) : tk.Label(
                master=self,
                image=self.parent.empty_image,
                text=c.NEG_CIRCLED_NUMBERS.get(num),
                font=('tkDefaultFont', 12),
                compound='c',
                width=16,
                height=12,
                fg=NumbHelper.FLAG_INACTIVE
            ) for num in range(1, 11) for count in range(self.nrows if num < 10 else self.nrows * 4)
        }
        for (num, count), lbl in self.lbls.items():
            num -= 1
            count -= 1
            if num < 9: # no longer checking 10 because of count -=1
                lbl.grid(row=count, column=num)
            else:
                lbl.grid(row=count // 4, column=num + count % 4)

    def change_flag(self, num, change):
        if self.exists:
            tracker = self.trackers.get(num)
            tracker.change(change)
            cfg = self.tracker_configs.get(change)
            if tracker.total == tracker.maximum + cfg.max_check:
                self.update_batch(num, cfg.over_state)
            elif not tracker.over:
                lbl = self.lbls.get((num, tracker.total + cfg.tracked_num))
                lbl.config(fg=cfg.flag_state)

    def guessed_flag(self, num, guess_safe=None):
        if self.exists:
            tracker = self.trackers.get(num)
            tracker.lock() if guess_safe else tracker.blew()
            revealed = tracker.blew_count + tracker.lock_count
            lbl = self.lbls.get((num, revealed))
            lbl.config(fg=NumbHelper.FLAG_LOCK if guess_safe else NumbHelper.FLAG_BLEW)
            if tracker.flag_count > 0:
                for flag in range(tracker.flag_count):
                    try:
                        self.lbls.get((num, revealed + flag + 1)).config(fg=NumbHelper.FLAG_ACTIVE)
                    except AttributeError:
                        self.update_batch(num, NumbHelper.FLAG_OVER)
                        break
            
    def update_batch(self, num, colour):
        for i in range(self.nrows * (4 if num >= 10 else 1)):
            self.lbls.get((num, i + 1)).config(bg=colour)
            
    def destroy(self):
        self.exists = False
        super().destroy()

def run():
    gui = GUI()
    gui.run()