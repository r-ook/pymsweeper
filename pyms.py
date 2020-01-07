from random import shuffle, randrange
from collections import namedtuple
from tkinter import messagebox
from time import time

import tkinter as tk

# Mouse state constants
MOUSE_LEFT = 2 ** 8
MOUSE_MID = 2 ** 9
MOUSE_RIGHT = 2 ** 10

# Status constants
STATUS = namedtuple('STATUS', 'icon fg bg')
STATUS_OKAY = STATUS('☺', 'black', 'gold')
STATUS_BOOM = STATUS('☠', 'white', 'red3')
STATUS_YEAH = STATUS('✌', 'white', 'limegreen')

# Mode constants
MODE_CONFIG = namedtuple('MODE_CONFIG', 'name x y rate amount special')
MODES = {
    0: MODE_CONFIG('Fresh', 8, 8, None, 10, False),
    1: MODE_CONFIG('Skilled', 16, 16, None, 40, False),
    2: MODE_CONFIG('Pro', 30, 16, None, 99, False),
    3: MODE_CONFIG('Half Deck', 12, 12, None, 52 // 2, True),
    4: MODE_CONFIG('Full Deck', 16, 16, None, 52, True),
    5: MODE_CONFIG('Double Deck', 28, 16, None, 52 * 2, True)
}

# Circled Number constants

# CIRCLED_NUMBERS = {i + 1: chr(0x2780 + i) for i in range(10)}
CIRCLED_NUMBERS = {i + 1: chr(0x2460 + i) for i in range(10)}

# NEG_CIRCLED_NUMBERS = {i + 1: chr(0x2776 + i) for i in range(10)}
NEG_CIRCLED_NUMBERS = {i + 1: chr(0x278A + i) for i in range(10)}

TRACKER_CONFIG = namedtuple('TrackerConfig', 'max_check over_state tracked_num flag_state')

class myIntVar(tk.IntVar):
    ''' Quick subclassing '''
    def increase(self, num=1):
        self.change(num)

    def decrease(self, num=1):
        self.change(-num)

    def change(self, num):
        self.set(self.get() + num)

class GUI(tk.Tk):
    ''' Main tkinter class that hosts window configs '''
    Options = namedtuple('Options', 'sound mouseover tracker allow_hits')

    def __init__(self):
        super().__init__()
        self.title('Pysweeper')
        self.empty_image = tk.PhotoImage(width=1, height=1)     # generic image to force size on button widgets
        self.var_mode = tk.IntVar(value=3)
        # self.var_mode.set(3)
        self.options = GUI.Options(*(tk.BooleanVar(name=opt_name) for opt_name in ('Warning Sound', 'Mouseover Hint', 'Flags Tracker', 'Allow Hits')))
        self.options.sound.set(False)
        for _bool, _opt in enumerate(self.options):
            _opt.set(int(_bool))
            _opt.trace('w', lambda *_, opt=_opt: self.option_callback(opt))
        # self.options.mouseover.set(True)
        # self.options.tracker.set(True)
        # self.options.allow_hits.set(True)
        # self.options.mouseover.trace('w', lambda *_, opt=self.options.mouseover: self.option_callback(opt))
        # self.options.tracker.trace('w', lambda *_, opt=self.options.tracker: self.option_callback(opt))
        # self.options.allow_hits.trace('w', lambda *_, opt=self.options.allow_hits: self.option_callback(opt))

        self.create_menus()
        self.taco_bell(self.options.sound.get())
        self.timer = Timer(self)
        self.field = None
        self.frm_main = tk.Frame(self)
        self.frm_helper = tk.Frame(self)
        self.hinter = HintBar(self, self.frm_helper)
        self.clueshelper = NumbHelper(self, self.frm_helper)

        # Build the main frames
        self.build_status_bar()
        self.frm_main.grid(row=1, column=0, sticky=tk.NSEW)
        self.frm_helper.grid(row=2, column=0, sticky=tk.NSEW)
        self.frm_helper.grid_columnconfigure(index=0, weight=1)
        self.frm_helper.bind('<Expose>', self.widget_exposed)
        self.hinter.build()
        self.build_field(MODES.get(self.var_mode.get()))

    def taco_bell(self, state):
        self.bell = super().bell if state else lambda: None

    def check_allow_hits(self, state):
        if state and self.var_mode.get() >= 3:
            self.frm_IEDs.grid_configure(columnspan=1)
            self.frm_blew.grid()
        else:
            self.frm_IEDs.grid_configure(columnspan=2)
            self.frm_blew.grid_remove()
        # change the current threshold if field exists
        try:
            self.field.allow_threshold(state)
        except AttributeError:
            pass

    def option_callback(self, opt):
        # Callback option to hide/unhide helpers
        # Using id(...) to overcome the unhashable tk Vars
        parser = {
            id(self.options.sound): self.taco_bell,
            id(self.options.mouseover): self.hinter.show,
            id(self.options.tracker): self.clueshelper.show,
            id(self.options.allow_hits): self.check_allow_hits    # getattr(self.field, 'allow_threshold', lambda _: None)
        }
        parser[id(opt)](opt.get())

    def widget_exposed(self, evt=None):
        if not any(child.winfo_viewable() for child in evt.widget.children.values()):
            evt.widget.config(height=1)

    def create_menus(self):
        # Setting up menus...
        menubar = tk.Menu(self)
        norm_modes = tk.Menu(self, tearoff=0)
        numb_modes = tk.Menu(self, tearoff=0)

        # Setting the modes...
        for idx, mode in MODES.items():
            mode_menu = numb_modes if mode.special else norm_modes
            mode_menu.add_radiobutton(
                label=mode.name,
                value=idx,
                variable=self.var_mode,
                command=lambda build_mode=mode: self.build_field(build_mode)
            )

        # Adding difficulty menu...
        diff_menu = tk.Menu(self, tearoff=0)
        diff_menu.add_cascade(label='Normal', menu=norm_modes)
        diff_menu.add_cascade(label='Hybrid', menu=numb_modes)
        
        # Adding option menu...
        self.options_menu = tk.Menu(self, tearoff=0)
        self.special_menu = tk.Menu(self, tearoff=0)
        options = iter(self.options)
        sound = next(options)
        self.options_menu.add_checkbutton(label=sound._name, variable=sound)
        for opt in options:
            self.special_menu.add_checkbutton(label=opt._name, variable=opt)
        self.options_menu.add_cascade(label='Hybrid', menu=self.special_menu)

        # Compile the menus together...
        menubar.add_cascade(label='Modes', menu=diff_menu)
        menubar.add_cascade(label='Options', menu=self.options_menu)
        self.config(menu=menubar)

    def build_status_bar(self):
        # Create all the widgets and frames...
        self.frm_status = tk.Frame(self)
        self.frm_timer = tk.LabelFrame(self.frm_status, text='Time:')
        self.lbl_timer = tk.Label(self.frm_timer, textvariable=self.timer.string)
        self.btn_main = tk.Button(
            self.frm_status,
            image=self.empty_image,
            command=lambda: self.build_field(MODES.get(self.var_mode.get())),
            font=('tkDefaultFont', 18, 'bold'),
            width=32,
            height=32,
            compound='c',
            relief=tk.GROOVE
        )
        self.update_status(STATUS_OKAY)
        self.frm_IEDs = tk.LabelFrame(self.frm_status, text='IEDs:')
        self.lbl_IEDs = tk.Label(self.frm_IEDs, text='0')
        self.frm_blew = tk.LabelFrame(self.frm_status, text='Hits:')
        self.lbl_blew = tk.Label(self.frm_blew, text='0') 
        
        # Grid management... ugh
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

    def build_field(self, mode:MODE_CONFIG):
        # seperate the special mode later....
        if mode.special:
            self.clueshelper.build(mode.amount // 13)
            self.options_menu.entryconfig('Hybrid', state=tk.NORMAL)
            for opt in (self.options.mouseover, self.options.tracker):
                # self.options_menu.entryconfig(opt._name, state=tk.NORMAL)
                self.option_callback(opt)
        else:
            self.options_menu.entryconfig('Hybrid', state=tk.DISABLED)
            # self.options_menu.entryconfig(self.options.mouseover._name, state=tk.DISABLED)
            # self.options_menu.entryconfig(self.options.tracker._name, state=tk.DISABLED)
            if self.hinter.exists:
                self.hinter.show(False)
            if self.clueshelper.exists:
                self.clueshelper.destroy()
        self.check_allow_hits(self.options.allow_hits.get())
        if not self.field is None:
            self.field.destroy()
        self.field = Field(self, mode)
        self.field.build()
        self.lbl_IEDs.config(textvariable=self.field.IED_current)
        self.lbl_blew.config(textvariable=self.field.IED_blew)
        self.update_status(STATUS_OKAY)
        self.timer.reset()

    def update_status(self, status:STATUS):
        ''' Update main happy face button '''
        self.btn_main.config(
            text=status.icon,
            fg=status.fg,
            bg=status.bg
        )

    def run(self):
        self.mainloop()        

class Timer:
    ''' Timer object to manage... the timer... '''
    # TODO Occassionally the update will not cancel the last job... need to investigate
    def __init__(self, parent):
        self.parent = parent
        self.string = tk.StringVar()
        self._job = None
        self.reset()

    def stop_update(self):
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
        self._update()

    def _update(self):
        self.to_string()
        if not self.parent.field.is_over:
            self._job = self.parent.after(ms=1000, func=self._update)

    def to_string(self):
        current = time() - self.start_time
        h, m, s = int(current // 3600), int(current % 3600 // 60), int(current % 60)
        self.string.set(f'{h:02}:{m:02}:{s:02}')

    def stop(self):
        self.end_time = time() - self.start_time
        self.to_string()
        self.stop_update()


class Field:
    def __init__(self, parent:tk.Toplevel, mode:MODE_CONFIG=MODES.get(0)):
        self.parent = parent
        self.mode = mode
        self.frame = tk.Frame(master=self.parent.frm_main)
        self.is_over = False
        if self.mode.amount:
            self.IED_count = self.mode.amount
        else:
            self.IED_count = int(self.mode.x * self.mode.y * self.mode.rate)
        self.IED_current = myIntVar(value=self.IED_count) # tk.IntVar()
        # self.IED_current.set(self.IED_count)
        self.IEDs = set()
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
        self.IED_blew = myIntVar(value=0) # tk.IntVar()
        self.map_goal = self.mode.x * self.mode.y - self.IED_count

    def allow_threshold(self, state=True):
        self.IED_threshold = 21 if state else 0

    def build(self):
        for elem in self.map.values():
            elem.build_surprise_box()
        self.frame.pack_propagate(False)
        self.frame.pack()

    def set_IEDs(self, current_coord: tuple = None):
        while len(self.IEDs) < self.IED_count:
            coord = (randrange(self.mode.x), randrange(self.mode.y))
            if coord != current_coord:
                self.IEDs.add(coord)
        if self.mode.special:
            cards = list(range(1, 10)) + [10] * 4
            cards = cards * (self.mode.amount // 13)
            shuffle(cards)
            for IED in self.IEDs:
                self.map.get(IED).is_IED = cards.pop()
        else:
            for IED in self.IEDs:
                self.map.get(IED).is_IED = 1
        self.parent.timer.start()

    def check_threshold(self, elem): 
        ''' Check if threshold is met '''
        # self.IED_blew.set(self.IED_blew.get() + elem.is_IED)
        self.IED_current.decrease()
        self.IED_blew.increase(elem.is_IED)
        if self.IED_blew.get() > self.IED_threshold:
            self.bewm(elem)

    def bewm(self, last):
        ''' When the field blows up '''
        self.parent.timer.stop()
        last.is_final()
        self.parent.update_status(STATUS_BOOM)
        self.is_over = True
        for IED in self.IEDs:
            self.map.get(IED).reveal() #.guess()
        for elem in self.map.values():
            if elem.flagged:
                elem.check_false_flag()
        # messagebox.showwarning('Oh no!', 'You done goofed!')

    def check_clear(self):
        ''' Check for when the field is cleared '''
        self.map_cleared += 1
        if self.map_cleared >= self.map_goal:
            self.parent.timer.stop()
            self.is_over = True
            self.parent.update_status(STATUS_YEAH)
            for elem in self.map.values():
                elem.reveal(is_over=True)
            congrats = 'You did it!'
            if self.IED_threshold > 0:
                hit = self.IED_blew.get()
                if hit:
                    congrats += f'\n... But you revealed {hit} point{"s" if hit > 1 else ""}.\nAim for 0 next time!'
                else:
                    congrats += f'\nAnd you managed to remain clear without revealing any mines.\nCongrats!'
            messagebox.showinfo('S U B A R A S H I!', congrats)
   
    def destroy(self):
        self.frame.destroy()

def gradient_colour(main:int, increm=0x080808, n=8, darken=True, as_string=False) -> list:
    if isinstance(main, str):
        try:
            main = int(main, 16)
        except ValueError:
            return []
    if as_string:
        colours = [f'#{main + (-i if darken else i) * increm:06x}' for i in range(n)]
    else:
        colours = [main + (-i if darken else i) * increm for i in range(n)]
    return colours

def zip_gradient(colours:list, **kwargs):
    kwargs = {kw: val for kw, val in kwargs.items() if kw in ('increm', 'n', 'darken', 'as_string')}
    grads = [gradient_colour(c, **kwargs) for c in colours]
    return list(zip(*grads))

class MapElem:
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
    def __init__(self, field, coord): #, val=0):
        self.field = field
        self.coord = coord
        self.frame = tk.Frame(self.field.frame, width=24, height=24)
        self.frame.pack_propagate(False)
        self.is_IED = 0
        self.clue = 0
        self.__flagged = 0
        self.revealed = False
        self.clueshelper = self.field.parent.clueshelper
        self.box = None
        self.lbl = None
        self._adjacents = None

    @property
    def flagged(self):
        return self.__flagged
    
    @flagged.setter
    def flagged(self, num):
        for i, check in enumerate((self.__flagged, num)):
            i = i * 2 - 1   # so that 0 = -1, 1 = 1
            if check != 0:
                self.clueshelper.change_flag(check, i)      
            else:
                self.field.IED_current.change(i) 
        self.__flagged = num

    def get_flag_config(self, num=None):
        return {'text': '⚑'}

    def flag(self, num=None):
        if num is None:
            num = 1
        if self.flagged == num:
            self.box.config(text=' ')
            self.flagged = 0
        else:
            self.box.config(**self.get_flag_config(num))
            self.flagged = num

    def check_false_flag(self):
        if not self.is_IED:
            self.box.config(**self.get_false_guess_config())

    def get_false_guess_config(self):
        return {'text': '❌', 'fg': 'white', 'bg': 'maroon'}

    def build(self, widget):
        self.frame.grid(row=self.coord[1], column=self.coord[0], sticky=tk.NSEW)
        widget.pack()

    def build_surprise_box(self):
        self.box = Surprise(self)
        self.build(self.box)
        return self.box

    @property
    def adjacents(self):
        if self._adjacents is None:
            cx, cy = self.coord
            mapper = self.field.map
            self._adjacents = [mapper.get((rx, ry)) for rx in range(cx-1, cx+2) for ry in range(cy-1, cy+2) if mapper.get((rx, ry))]
        return self._adjacents

    def adjacent_IEDs(self):
        # if not self.is_IED:
        #     self.clue = sum(adj.is_IED for adj in self.adjacents)
        # return self.clue
        if self.is_IED:
            return 0
        else:
            return sum(adj.is_IED for adj in self.adjacents)

    def adjacent_flags(self):
        return sum(adj.flagged + (adj.is_IED * int(adj.revealed)) for adj in self.adjacents)

    def get_IED_config(self, final=False):
        config = {
            True: {'text': '✨', 'fg': 'red'},
            False: {'text' : '☀'}
        }.get(final)
        config.update({'font' : ('tkDefaultFont', 12, 'bold')})
        return config

    def is_final(self):
        if self.is_IED:
            self.lbl.config(**self.get_IED_config(final=True))
        else:
            self.lbl.config(**self.get_false_guess_config())
            if self.clue:
                self.lbl.config(text=self.clue)

    def label_actual(self):
        if self.is_IED:
            actual = self.get_IED_config()
        else:
            actual = {
                'text' : self.clue if self.clue else '',
                'fg' : self.__class__.clue_colours.get(self.clue, 'SystemButtonText'),
                'font' : ('tkDefaultFont', 10, 'bold'),
            }

        lbl = tk.Label(master=self.frame, **actual)
        return lbl

    def create_actual(self):
        self.lbl = self.label_actual()
        if self.is_IED == 0:
            self.lbl.bind('<ButtonRelease-1>', self.omni_click)
            self.lbl.bind('<ButtonRelease-3>', self.omni_click)
        self.lbl.pack(fill=tk.BOTH, expand=True)

    def guess(self, safe=None):
        # if (self.flagged == 0 and not self.revealed) or safe is not None:
        if not self.revealed:
            if self.flagged == 0 or safe is not None:
                if self.field.map_cleared == 0:
                    self.field.set_IEDs(self.coord)
                self.reveal(safe=safe)
                if self.clue == 0 and not self.is_IED:
                    for adj in self.adjacents:
                        adj.guess()
                # if not self.field.is_over:
                #     if self.is_IED and not safe:
                #         self.field.check_threshold(self)
                #     elif self.is_IED == 0:
                #         if safe is False:
                #             self.field.bewm(self)
                #         else:
                #             self.field.check_clear()
                if not safe:
                    if self.is_IED:
                        self.field.check_threshold(self)
                    elif safe is False:
                        self.field.bewm(self)
                    else:
                        self.field.check_clear()

    def reveal(self, safe=False, is_over=False):
        if self.flagged:
            self.flagged = 0
        self.revealed = True
        self.clue = self.adjacent_IEDs()
        self.create_actual()
        if safe or is_over:
            self.lbl.config(bg='lightblue')
        self.box.pack_forget()

    def omni_click(self, evt, ignore=False):
        if self.field.is_over:
            return
        w, h = evt.widget.winfo_geometry().replace('+', 'x').split('x')[:2]
        if evt.x in range(int(w)) and evt.y in range(int(h)):
            if (evt.num == 1 and evt.state & MOUSE_RIGHT) or (evt.num == 3 and evt.state & MOUSE_LEFT):
                self.both_release()
            elif evt.num == 1:
                self.left_release()
            elif evt.num == 2:
                if self.flagged:
                    self.guess(safe=self.flagged == self.is_IED)
            elif evt.num == 3 and not ignore:
                self.right_release()

    def left_release(self):
        self.guess()

    def right_release(self):
        ### still trying to figure out if right release can be separated from right click for fast flagging
        # unheld = (evt.state & MOUSE_LEFT > 0) if evt else True
        # if not self.revealed and unheld:
        if not self.revealed:
            self.flag()

    def both_release(self, *evt):
        if self.adjacent_flags() == self.clue and self.revealed:
            self.guess()
            for adj in self.adjacents:
                adj.guess()
        else:
            self.field.parent.bell()

class NumbedMapElem(MapElem):
    val_colours = MapElem.clue_colours
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
        if not self.revealed:
            self.flag((self.flagged + 1) % 11)

    def get_IED_config(self, final=False):
        config = {
            'text' : NEG_CIRCLED_NUMBERS.get(self.is_IED),
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
    
    def get_flag_config(self, num):
        return {
            'text': CIRCLED_NUMBERS.get(num, ' '),
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
        self.build(self.box)
        return self.box
    
    def check_false_flag(self):
        if self.flagged != self.is_IED:
            self.box.config(**self.get_IED_config())
            self.box.config(bg='orange')
        super().check_false_flag()


class Surprise(tk.Button):
    ''' Concealer button object to handle flagging '''

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
        # self.bind('<ButtonRelease-3>', lambda e: self.parent.omni_click(e, ignore=True))

        # NUM binding
        for i, s in enumerate('1234567890', 1):
            if i > 10: i = 10
            self.bind(s, lambda e, x=i: self.flag(x))

        # WASD binding
        for i, s in enumerate('qweasdzxc', 4):
            if i > 10: i = 10
            self.bind(s, lambda e, x=i: self.flag(x))
            self.bind(s.upper(), lambda e, x=i: self.flag(x))

class HintBar(tk.Frame):
    Hint = namedtuple('Hint', 'frame label counter')
    def __init__(self, gui: GUI, parent_frame):
        self.gui = gui
        self.parent_frame = parent_frame
        self.exists = False    
    
    def build(self):
        if self.exists:
            self.destroy()
        super().__init__(master=self.parent_frame)
        self.hints = {
            k: self.create_inner_frame(k)
            for k in ('Total', 'Flagged/Hits', 'Remaining')
        }
        for i, hint in enumerate(self.hints.values()):
            hint.frame.grid(row=0, column=i, sticky=tk.NSEW)
            hint.label.pack(fill=tk.BOTH, expand=True)
        for i in range(3):
            self.columnconfigure(index=i, weight=1)
        self.exists = True

    def show(self, state):
        self.grid(row=0, column=0, sticky=tk.NSEW) if state else self.grid_remove()

    def create_inner_frame(self, ctype):
        def validate(hinter):
            if hinter.counter.get() < 0:
                hinter.label.config(bg='yellow')
            else:
                hinter.label.config(bg='SystemButtonFace')
        frame = tk.LabelFrame(master=self, text=f'{ctype}:')
        counter = tk.IntVar()
        label = tk.Label(master=frame, textvariable=counter)
        hinter = HintBar.Hint(frame, label, counter)
        counter.trace('w', lambda *args: validate(hinter))
        return hinter

    def update(self, hinter:NumbedMapElem):
        if not self.gui.field.is_over:
            total = hinter.clue
            flags_hits = hinter.adjacent_flags()
            remaining = total - flags_hits
            self.hints['Total'].counter.set(total)
            self.hints['Flagged/Hits'].counter.set(flags_hits)
            self.hints['Remaining'].counter.set(remaining)

    def reset(self, *args):
        if not self.gui.field.is_over:
            for hint in self.hints.values():
                hint.counter.set(0)

    def destroy(self):
        self.exists = False
        super().destroy()

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

    # def cumsum(self, n=3):
    #     return sum((self.blew_count, self.lock_count, self.flag_count)[:n])

    def change(self, change=1):
        self.flag_count = max(0, self.flag_count + change)

    def blew(self):
        self.blew_count += 1
    
    def lock(self):
        self.lock_count += 1

    def __iter__(self):
        return (sum((self.blew_count, self.lock_count, self.flag_count)[:i]) for i in range(1, 4))


class NumbHelper(tk.Frame):
    ''' Helper Frame object to help track flags '''
    FLAG_ACTIVE = 'forestgreen'
    FLAG_LOCK = 'dodger blue'
    FLAG_BLEW = 'red2'
    FLAG_OVER = 'gold'
    FLAG_OKAY = 'SystemButtonFace'
    FLAG_INACTIVE = 'LightCyan3'
    CONFIGS = {
        1: TRACKER_CONFIG(1, FLAG_OVER, 0, FLAG_ACTIVE),
        -1: TRACKER_CONFIG(0, FLAG_OKAY, 1, FLAG_INACTIVE)
    }
    def __init__(self, parent, parent_frame):
        self.parent = parent
        self.parent_frame = parent_frame
        self.nrows = None
        self.trackers = None
        self.exists = False

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
                text=NEG_CIRCLED_NUMBERS.get(num),
                font=('tkDefaultFont', 12),
                compound='c',
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
            cfg = NumbHelper.CONFIGS.get(change)
            if tracker.flag_count == tracker.maximum + cfg.max_check:
                self.update_batch(num, cfg.over_state)
            elif not tracker.over:
                lbl = self.lbls.get((num, tracker.flag_count + cfg.tracked_num))
                lbl.config(fg=cfg.flag_state)

    def guessed_flag(self, num, safe=False):
        if safe:
            tracker = self.trackers.get(num)
            tracker.lock()
        

            
    def update_batch(self, num, colour):
        for i in range(self.nrows * (4 if num >= 10 else 1)):
            self.lbls.get((num, i + 1)).config(bg=colour)
            
    def destroy(self):
        self.exists = False
        super().destroy()


if __name__ == '__main__':
    gui = GUI()
    gui.run()
