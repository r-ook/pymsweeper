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
CIRCLED_NUMBERS = {
    1 : '①',
    2 : '②',
    3 : '③',
    4 : '④',
    5 : '⑤',
    6 : '⑥',
    7 : '⑦',
    8 : '⑧',
    9 : '⑨',
    10 : '⑩'
}

NEG_CIRCLED_NUMBERS = {
    1 : '❶',
    2 : '❷',
    3 : '❸',
    4 : '❹',
    5 : '❺',
    6 : '❻',
    7 : '❼',
    8 : '❽',
    9 : '❾',
    10 : '❿'
}

class GUI(tk.Tk):
    ''' Main tkinter class that hosts window configs '''

    def __init__(self):
        super().__init__()
        self.title('Pysweeper')
        self.empty_image = tk.PhotoImage(width=1, height=1)     # generic image to force size on button widgets
        self.var_mode = tk.IntVar()
        self.var_mode.set(0)
        self.var_sound = tk.BooleanVar()
        self.var_sound.set(False)
        self.create_menus()
        self.timer = Timer(self)
        self.field = None
        self.frm_main = tk.Frame(self)
        self.frm_helper = tk.Frame(self)
        self.clueshelper = NumbHelper(self, self.frm_helper)
        self.hinter = HintBar(self, self.frm_helper)
        self.build_status_bar()
        self.frm_main.grid(row=1, column=0, sticky=tk.NSEW)
        self.frm_helper.grid(row=2, column=0, sticky=tk.NSEW)

    def create_menus(self):
        menubar = tk.Menu(self)
        norm_modes = tk.Menu(self, tearoff=0)
        numb_modes = tk.Menu(self, tearoff=0)
        for idx, mode in MODES.items():
            mode_menu = numb_modes if mode.special else norm_modes
            mode_menu.add_radiobutton(
                label=mode.name,
                value=idx,
                variable=self.var_mode,
                command=lambda build_mode=mode: self.build_field(build_mode)
            )
        diff_menu = tk.Menu(self, tearoff=0)
        diff_menu.add_cascade(label='Normal', menu=norm_modes)
        diff_menu.add_cascade(label='Hybrid', menu=numb_modes)
        option_menu = tk.Menu(self, tearoff=0)
        option_menu.add_checkbutton(
            label='Warning Sound',
            variable=self.var_sound
        )
        menubar.add_cascade(label='Modes', menu=diff_menu)
        menubar.add_cascade(label='Options', menu=option_menu)
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
        
        # Grid management... ugh
        self.frm_status.grid(row=0, column=0, sticky=tk.NSEW)
        self.frm_status.columnconfigure(index=0, weight=3)
        self.frm_status.columnconfigure(index=1, weight=1)
        self.frm_status.columnconfigure(index=2, weight=3)
        self.frm_timer.grid(row=0, column=0, sticky=tk.NSEW)
        self.btn_main.grid(row=0, column=1, sticky=tk.NS)
        self.frm_IEDs.grid(row=0, column=2, sticky=tk.NSEW)
        self.lbl_timer.pack()
        self.lbl_IEDs.pack()

    def build_field(self, mode:MODE_CONFIG):
        # seperate the special mode later....
        if mode.special:
            self.frm_helper.grid()
            if not self.hinter.exists:
                self.hinter.build()
            if self.clueshelper.exists:
                self.clueshelper.destroy()
            self.clueshelper.build(mode.amount // 13)
        else:
            if self.hinter.exists:
                self.hinter.destroy()
            if self.clueshelper.exists:
                self.clueshelper.destroy()
            self.frm_helper.grid_remove()
        if not self.field is None:
            self.field.destroy()
        self.field = Field(self, mode)
        self.field.build()
        self.lbl_IEDs.config(textvariable=self.field.IED_current)
        self.update_status(STATUS_OKAY)
        self.timer.start()

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
    def __init__(self, parent):
        self.parent = parent
        self.string = tk.StringVar()
        self.string.set('00:00:00')
        self.start_time = None
        self.end_time = None
        self._job = None

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
        self.parent.after_cancel(self._job)
        # return self.end_time


class Field:
    def __init__(self, parent:tk.Toplevel, mode:MODE_CONFIG=MODES.get(0)): # dimension:DIMENSION=DIMENSION(16, 16), rate:float=.15, amount=40):
        self.parent = parent
        self.mode = mode
        self.frame = tk.Frame(master=self.parent.frm_main)
        self.is_over = False
        if self.mode.amount:
            self.IED_count = self.mode.amount
        else:
            self.IED_count = int(self.mode.x * self.mode.y * self.mode.rate)
        self.IED_current = tk.IntVar()
        self.IED_current.set(self.IED_count)
        self.map_cleared = 0
        self.map = {
            (x, y): MapNumbedElem(self, (x, y)) if self.mode.special else MapElem(self, (x, y)) 
            # MapIED(self, (x, y), 1) if (x, y) in self.IEDs else MapElem(self, (x, y))
            # MapElem(self, (x, y), 'X' if (x, y) in self.IEDs else None)
            for x in range(self.mode.x)
            for y in range(self.mode.y)
        }
        self.IEDs = set()
        self.map_goal = self.mode.x * self.mode.y - self.IED_count

    def build(self):
        for elem in self.map.values():
            elem.build_surprise_box()
        self.frame.pack_propagate(False)
        self.frame.pack()

    def set_IEDs(self, current_coord:tuple=None):
        while len(self.IEDs) < self.IED_count:
            coord = (randrange(self.mode.x), randrange(self.mode.y))
            if coord != current_coord:
                self.IEDs.add(coord)
        if self.mode.special:
            cards = list(range(1, 10)) + [10] * 4
            cards = cards * (self.mode.amount // 13)
            shuffle(cards)
            for IED in self.IEDs:
                self.map.get(IED).val = cards.pop()
        else:
            for IED in self.IEDs:
                self.map.get(IED).is_IED = True

    def oops(self):
        ''' When the field blows up '''
        self.parent.timer.stop()
        self.parent.update_status(STATUS_BOOM)
        self.is_over = True
        for IED in self.IEDs:
            self.map.get(IED).reveal()
        for elem in self.map.values():
            if elem.flagged:
                elem.box.check_false_flag()
        messagebox.showwarning('Oh no!', 'You done goofed!')

    def check_clear(self):
        ''' Check for when the field is cleared '''
        self.map_cleared += 1
        if self.map_cleared >= self.map_goal:
            self.parent.timer.stop()
            self.is_over = True
            self.parent.update_status(STATUS_YEAH)
            ### TODO implement revealing of showing IEDs
            for elem in self.map.values():
                elem.just_reveal(safe=True)
            messagebox.showinfo('Subarashi!', 'You did it!')
   
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
    def __init__(self, field, coord, val=0):
        self.field = field
        self.coord = coord
        self.frame = tk.Frame(self.field.frame, width=24, height=24)
        self.frame.pack_propagate(False)
        self.val = val
        # self.colour = MapElem.clue_colours.get(val, 'SystemButtonText')
        # self.is_IED = True if val else False
        self.clue = 0
        self.flagged = 0
        self.revealed = False
        self.box = None
        self.lbl = None

    @property
    def is_IED(self):
        return True if self.val else False
    
    @is_IED.setter
    def is_IED(self, value):
        self.val = 1 if value else 0

    def build(self, widget): # widget:tk.Widget):
        self.frame.grid(row=self.coord[1], column=self.coord[0], sticky=tk.NSEW)
        widget.pack()

    def build_surprise_box(self):
        self.box = Surprise(self)
        self.build(self.box)
        return self.box

    def count_adjacent_IEDs(self):
        if not self.is_IED:
            self.clue = sum(adj.val for adj in self.adjacents())
        return self.clue

    def adjacents(self):
        cx, cy = self.coord
        mapper = self.field.map
        return (mapper.get((rx, ry)) for rx in range(cx-1, cx+2) for ry in range(cy-1, cy+2) if mapper.get((rx, ry)))

    def get_IED_config(self):
        config = {
            'text' : '☀' if self.field.is_over else '✨',   #'☀'
            'fg' : 'SystemButtonText' if self.field.is_over else 'red',
            'font' : ('tkDefaultFont', 12, 'bold')
        }
        return config # '✹' if self.field.is_over else '✨'   #'☀'

    def label_actual(self):
        if self.is_IED:
            actual = self.get_IED_config()
        else:
            actual = {
                'text' : self.clue if self.clue else '',
                'fg' : self.__class__.clue_colours.get(self.clue, 'SystemButtonText'),
                'font' : ('tkDefaultFont', 10, 'bold'),
            }
            # actual = self.get_IED_text() if self.is_IED else self.clue if self.clue else ''
        lbl = tk.Label(
            master=self.frame,
            # text=actual, # '✹' if self.val else self.clue if self.clue else '',
            # fg=self.__class__.clue_colours.get(self.clue, 'SystemButtonText'),
            **actual
        )
        return lbl

    def create_actual(self):
        self.lbl = self.label_actual()
        self.lbl.bind('<ButtonRelease-1>', self.omni_click)
        self.lbl.bind('<ButtonRelease-3>', self.omni_click)
        self.lbl.pack()

    def reveal(self):
        if self.field.map_cleared == 0:
            self.field.set_IEDs(self.coord)
        # if not self.revealed and self.flagged == 0:
        go_ahead = self.just_reveal()
        if go_ahead:
            if self.clue == 0 and not self.is_IED:
                for elem in self.adjacents():
                    elem.reveal()
            if not self.field.is_over:
                if self.is_IED:
                    self.field.oops()
                else:
                    self.field.check_clear()

    def just_reveal(self, safe=False):
        go_ahead = self.flagged == 0 and not self.revealed
        if go_ahead:
            self.revealed = True
            self.count_adjacent_IEDs()
            self.create_actual()
            if safe:
                self.lbl.config(bg='lightblue')
            self.box.destroy()
        return go_ahead

    def __eq__(self, other):
        return self.val == other

    def omni_click(self, evt, ignore=False):
        if self.field.is_over:
            return
        w, h = evt.widget.winfo_geometry().replace('+', 'x').split('x')[:2]
        if evt.x in range(int(w)) and evt.y in range(int(h)):
            if (evt.num == 1 and evt.state & MOUSE_RIGHT) or (evt.num == 3 and evt.state & MOUSE_LEFT):
                self.both_release()
            elif evt.num == 1:
                self.left_release()
            elif evt.num == 3 and not ignore:
                self.right_release()

    def left_release(self):
        self.reveal()
    
    def right_release(self):
        ### still trying to figure out if right release can be separated from right click for fast flagging
        # unheld = (evt.state & MOUSE_LEFT > 0) if evt else True
        # if not self.revealed and unheld:
        if not self.revealed:
            # self.flagged = self.box.flag()
            self.box.flag()            

    def both_release(self, *evt):
        if self.adjacent_flags() == self.clue:
            self.reveal()
            for adj in self.adjacents():
                adj.reveal()
        else:
            if self.field.parent.var_sound.get():
                self.field.parent.bell()

    def adjacent_flags(self):
        return sum(adj.flagged for adj in self.adjacents())

class MapNumbedElem(MapElem):
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
    def get_IED_config(self):
        config = {
            'text' : NEG_CIRCLED_NUMBERS.get(self.val),
            'fg' : MapNumbedElem.val_colours.get(self.val) if self.field.is_over else 'white',
            'font' : ('tkDefaultFont', 12)
        }
        if not self.field.is_over:
            config.update(
                {
                    'bg': 'maroon',
                    'relief': tk.SUNKEN
                }
            )
        return config # MapNumbedElem.val_numbers.get(self.val)

    def create_actual(self):
        super().create_actual()
        self.lbl.bind('<Enter>', lambda e: self.field.parent.hinter.update(self))
        self.lbl.bind('<Leave>', self.field.parent.hinter.reset)

    def build_surprise_box(self):
        self.box = NumbedSurprise(self)
        self.build(self.box)
        return self.box


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
        self.flagged = 0
        self.bind('<ButtonRelease-1>', self.parent.omni_click)
        self.set_other_bindings()
    
    def set_other_bindings(self):
        self.bind('<ButtonRelease-3>', self.parent.omni_click)
        # self.bind('<Button-3>', parent.omni_click)

    def flag(self, num=None):
        if num is None:
            flag_config = {'text': '⚑'}
            num = 1
        else:
            flag_config = {
                'text': CIRCLED_NUMBERS.get(num),
                'fg': MapNumbedElem.val_colours.get(num),
                'font': ('tkDefaultFont', 12)
            }

        count = self.parent.field.IED_current.get()
        if self.flagged != 0:
            # Starting to feel like monkey patching now...
            getattr(self, 'remove_from_helper', lambda n: None)(self.flagged)
        if self.flagged == num:
            self.config(text=' ')    #, bg='SystemButtonFace')
            self.flagged = 0
            self.parent.field.IED_current.set(count + 1)
        else:
            self.config(**flag_config)
            if self.flagged == 0:
                self.parent.field.IED_current.set(count - 1)
            self.flagged = num
            getattr(self, 'add_to_helper', lambda n: None)(self.flagged)

        self.parent.flagged = self.flagged

    def check_false_flag(self):
        if not self.parent.is_IED:
            self.config(text='❌', fg='white', bg='maroon')


class NumbedSurprise(Surprise):
    ''' Subclass concealer button to handle additional flagging '''

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        clueshelper = self.parent.field.parent.clueshelper
        if clueshelper.exists:
            self.remove_from_helper = clueshelper.remove_flag
            self.add_to_helper = clueshelper.add_flag            

    def set_other_bindings(self):
        self.bind('<ButtonRelease-3>', lambda e: self.parent.omni_click(e, ignore=True))
        self.bind('<Enter>', lambda e: self.focus_set())
        self.bind('<Leave>', lambda e: self.parent.frame.focus_set())

        # NUM binding
        for i, s in enumerate('1234567890', 1):
            if i > 10: i = 10
            self.bind(s, lambda e, x=i: self.flag(x))

        # WASD binding
        for i, s in enumerate('qweasdzxc', 4):
            if i > 10: i = 10
            self.bind(s, lambda e, x=i: self.flag(x))
            self.bind(s.upper(), lambda e, x=i: self.flag(x))

    def check_false_flag(self):
        if self.flagged != self.parent.val:
            self.config(**self.parent.get_IED_config())
            self.config(bg='gold')
        super().check_false_flag()

class HintBar(tk.Frame):
    Hint = namedtuple('Hint', 'frame label counter')
    def __init__(self, gui:GUI, parent_frame):
        self.gui = gui
        self.parent_frame = parent_frame
        self.exists = False    
    
    def build(self):
        super().__init__(master=self.parent_frame)
        self.hints = {
            k: self.create_inner_frame(k)
            for k in ('Total', 'Flagged', 'Remaining')
        }
        for i, hint in enumerate(self.hints.values()):
            hint.frame.grid(row=0, column=i, sticky=tk.NSEW)
            hint.label.pack(fill=tk.BOTH, expand=True)
        self.pack(fill=tk.BOTH, expand=True)
        for i in range(3):
            self.columnconfigure(index=i, weight=1)
        self.exists = True

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

    def update(self, hinter:MapNumbedElem):
        if not self.gui.field.is_over:
            total = hinter.clue
            flags = hinter.adjacent_flags()
            remaining = total - flags
            self.hints['Total'].counter.set(total)
            self.hints['Flagged'].counter.set(flags)
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
        self.count = 0
        self.over = False
    
    def increase(self):
        if not self.over and self.count >= self.maximum:
            self.over = True
        self.count += 1
    
    def decrease(self):
        self.count = max(0, self.count - 1)
        if self.over and self.count <= self.maximum:
            self.over = False


class NumbHelper(tk.Frame):
    ''' Helper Frame object to help track flags '''
    FLAG_ACTIVE = 'green'
    FLAG_OVER = 'red'
    FLAG_INACTIVE = 'grey'
    def __init__(self, parent, parent_frame):
        self.parent = parent
        self.parent_frame = parent_frame
        self.nrows = None
        self.trackers = None
        self.exists = False
    
    def build(self, nrows):
        self.nrows = nrows
        self.trackers = {
            i: NumbTracker(self.nrows * (4 if i >= 10 else 1))
            for i in range(1, 11)
        }
        super().__init__(master=self.parent_frame)
        self.create_labels()
        self.pack()
        self.exists = True

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

    def add_flag(self, num):
        tracker = self.trackers.get(num)
        tracker.increase()
        if tracker.over:
            self.update_batch(num, NumbHelper.FLAG_OVER)
        else:
            lbl = self.lbls.get((num, tracker.count))
            lbl.config(fg=NumbHelper.FLAG_ACTIVE)

    def remove_flag(self, num):
        tracker = self.trackers.get(num)
        tracker.decrease()
        if not tracker.over:
            if tracker.count == tracker.maximum:
                self.update_batch(num, NumbHelper.FLAG_ACTIVE)
            else:
                lbl = self.lbls.get((num, tracker.count + 1))
                lbl.config(fg=NumbHelper.FLAG_INACTIVE)

    def update_batch(self, num, colour):
        for i in range(self.nrows * (4 if num >= 10 else 1)):
            self.lbls.get((num, i + 1)).config(fg=colour)
            
    def destroy(self):
        self.exists = False
        super().destroy()


if __name__ == '__main__':
    gui = GUI()
    gui.run()
    # root = tk.Tk()
    # root.empty_image = tk.PhotoImage(width=1, height=1)
    # nums = NumbHelper(root, root)
    # nums.build(4)
    # root.mainloop()
