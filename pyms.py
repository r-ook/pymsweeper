from random import shuffle, randrange
from collections import namedtuple
from tkinter import messagebox, font
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
MODE_CONFIG = namedtuple('MODE_CONFIG', 'x y rate amount special')
MODE = {
    0: MODE_CONFIG(8, 8, None, 10, False),
    1: MODE_CONFIG(16, 16, None, 40, False),
    2: MODE_CONFIG(30, 16, None, 99, False),
    3: MODE_CONFIG(10, 10, None, 52 // 2, True),
    4: MODE_CONFIG(16, 16, None, 52, True),
    5: MODE_CONFIG(24, 16, None, 52 * 2, True)
}

class GUI(tk.Tk):

    def __init__(self):
        super().__init__()
        # default_font = font.nametofont('TkDefaultFont')
        # default_font.configure(size=8)
        self.title('Pysweeper')
        self.menubar = tk.Menu(self)
        self.empty_image = tk.PhotoImage(width=1, height=1)
        self.var_mode = tk.IntVar()
        self.var_mode.set(0)
        self.var_sound = tk.BooleanVar()
        self.var_sound.set(False)

        def set_menu(modes, start=0):
            mode_menu = tk.Menu(self, tearoff=0)
            for i, mode in enumerate(modes, start):
                mode_menu.add_radiobutton(
                    label=mode,
                    value=i,
                    variable=self.var_mode,
                    command=lambda x=i: self.build_field(MODE.get(x))
                )
            return mode_menu

        norm_modes = set_menu(('Fresh', 'Skilled', 'Pro'), 0)
        numb_modes = set_menu(('Half Deck', 'Full Deck', 'Double Deck'), 3)
        diff_menu = tk.Menu(self, tearoff=0)
        diff_menu.add_cascade(label='Normal', menu=norm_modes)
        diff_menu.add_cascade(label='Hybrid', menu=numb_modes)
        option_menu = tk.Menu(self, tearoff=0)
        option_menu.add_checkbutton(
            label='Sound',
            variable=self.var_sound
        )
        self.menubar.add_cascade(label='Modes', menu=diff_menu)
        self.menubar.add_cascade(label='Options', menu=option_menu)
        self.config(menu=self.menubar)
        # self.face = tk.StringVar()
        # self.face.set(OKAY)
        self.timer = Timer(self)
        self.field = None
        self.build_status_bar()

    def build_status_bar(self):
        self.frm_status = tk.Frame(self) #, height=48)
        self.frm_timer = tk.LabelFrame(self.frm_status, text='Time:')
        self.lbl_timer = tk.Label(self.frm_timer, textvariable=self.timer.string)
        self.btn_main = tk.Button(
            self.frm_status,
            image=self.empty_image,
            command=lambda: self.build_field(MODE.get(self.var_mode.get())),
            font=('tkDefaultFont', 18, 'bold'),
            width=32,
            height=32,
            compound='c',
            relief=tk.GROOVE,
            anchor=tk.CENTER
        )
        self.update_status(STATUS_OKAY)
        self.frm_IEDs = tk.LabelFrame(self.frm_status, text='IEDs:')
        self.lbl_IEDs = tk.Label(self.frm_IEDs, text='0')
        
        # self.frm_status.grid_propagate(False)
        self.frm_status.pack(fill=tk.BOTH, expand=True)
        self.frm_status.columnconfigure(index=0, weight=3)
        self.frm_status.columnconfigure(index=1, weight=1)
        self.frm_status.columnconfigure(index=2, weight=3)
        self.frm_timer.grid(row=0, column=0, sticky=tk.NSEW)
        self.btn_main.grid(row=0, column=1, sticky=tk.NS)
        self.frm_IEDs.grid(row=0, column=2, sticky=tk.NSEW)
        self.lbl_timer.pack()
        self.lbl_IEDs.pack()

    def build_field(self, mode:MODE_CONFIG):
        if not self.field is None:
            self.field.destroy()
        self.field = Field(self, mode)
        self.field.build()
        # self.var_timer.set(0)
        self.lbl_IEDs.config(textvariable=self.field.IED_current)
        self.update_status(STATUS_OKAY)
        self.timer.start()

    def update_status(self, status:STATUS):
        self.btn_main.config(
            text=status.icon,
            fg=status.fg,
            bg=status.bg
        )

    # def timing(self):
    #     if not self.timed is None:
    #         self.after_cancel(self.timed)
    #     var_timer = self.var_timer.get()
    #     self.var_timer.set(var_timer + 1)
    #     self.timed = self.after(ms=1000, func=self.timing)


    def run(self):
        self.mainloop()        

class Timer:
    def __init__(self, master):
        self.master = master
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
        if not self.master.field.is_over:
            self._job = self.master.after(ms=1000, func=self._update)

    def to_string(self):
        # if val:
        #     current = val
        # else:
        current = time() - self.start_time
        h, m, s = int(current // 360), int(current % 360 // 60), int(current % 60)
        self.string.set(f'{h:02}:{m:02}:{s:02}')

    # def timetuple(self, precision=False):
    #     if precision:
    #         pass
    #     else:
    #         return int(current // 360), int(current % 360 // 60), int(current % 60)
    
    def stop(self):
        self.end_time = time() - self.start_time
        self.to_string()
        self.master.after_cancel(self._job)
        # return self.end_time


class Field:
    def __init__(self, master:tk.Toplevel, mode:MODE_CONFIG=MODE.get(0)): # dimension:DIMENSION=DIMENSION(16, 16), rate:float=.15, amount=40):
        self.master = master
        self.mode = mode
        self.frame = tk.Frame(master=self.master)
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
        # self.IEDs = set()
        while len(self.IEDs) < self.IED_count:
            coord = (randrange(self.mode.x), randrange(self.mode.y))
            if coord != current_coord:
                self.IEDs.add(coord)
        if self.mode.special:
            # testing blackjack mode...
            # cards = list(range(1, 10))*4 + [10]*16
            cards = list(range(1, 10)) + [10] * 4
            cards = cards * (self.mode.amount // 13)
            shuffle(cards)
            for IED in self.IEDs:
                self.map.get(IED).val = cards.pop()
        else:
            for IED in self.IEDs:
                self.map.get(IED).is_IED = True
        # return IEDs

    def oops(self):
        # if self.mode.special:
        #     return # TODO - remove after testing
        self.master.timer.stop()
        self.master.update_status(STATUS_BOOM)
        self.is_over = True
        for IED in self.IEDs:
            self.map.get(IED).reveal()
        for elem in self.map.values():
            if elem.flagged:
                elem.box.check_false_flag()
        messagebox.showwarning('Oh no!', 'You done goofed!')

    def check_clear(self):
        self.map_cleared += 1
        if self.map_cleared >= self.map_goal:
            self.master.timer.stop()
            self.master.update_status(STATUS_YEAH)
            # for elem in self.map.values():
            #     elem.reveal()
            self.is_over = True
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

def zip_gradient(colours:list, flatten=True, **kwargs):
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
        8: 'seashell4'
    }
    def __init__(self, field, coord, val=0):
        self.field = field
        self.coord = coord
        self.frame = tk.Frame(self.field.frame, width=24, height=24)
        self.frame.pack_propagate(False)
        self.val = val
        # self.colour = MapElem.clue_colours.get(val, 'SystemButtonText')
        # self.is_IED = True if val else False
        self.clue = None
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
        # if self.is_IED:
        #     # if self.field.mode.special:
        #     #     actual = MapElem.val_colours.get(self.val)
        #     # else:
        #     #     actual = '✹' if self.field.is_over else '✨'   #'☀'
        #     actual = self.get_IED_text()
        # else:
        #     actual = self.clue if self.clue else ''
        self.lbl = self.label_actual()
        self.lbl.bind('<ButtonRelease-1>', self.omni_click)
        self.lbl.bind('<ButtonRelease-3>', self.omni_click)
        self.lbl.pack()

    def reveal(self):
        if self.field.map_cleared == 0:
            self.field.set_IEDs(self.coord)
        if not self.revealed and self.flagged == 0:
            # if not self.is_IED:
            self.revealed = True
            self.count_adjacent_IEDs()
            self.create_actual()
            self.box.destroy()
            if self.clue == 0:
                for elem in self.adjacents():
                    elem.reveal()
            if not self.field.is_over:
                if self.is_IED:
                    # self.lbl.config(fg='red') #, text='✨')
                    self.field.oops()
                else:
                    self.field.check_clear()
            # return self.lbl

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
    
    def right_release(self, evt=None):
        # unheld = (evt.state & MOUSE_LEFT > 0) if evt else True
        # if not self.revealed and unheld:
        if not self.revealed:
            # self.flagged = self.box.flag()
            self.box.flag()

    def both_release(self, *evt):
        adjs = list(self.adjacents())
        flags = sum(adj.flagged for adj in adjs)
        if flags == self.clue:
            self.reveal()
            for adj in adjs:
                adj.reveal()
        else:
            if self.field.master.var_sound.get():
                self.field.master.bell()

class MapNumbedElem(MapElem):
    val_numbers = {
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
    val_colours = MapElem.clue_colours
    val_colours.update(
        {
            9: 'goldenrod',
            10: 'pink4'
        }
    )
    clue_colours = {
        i: clue_colour for i, clue_colour in enumerate(
            colour for c_set in zip_gradient(
                [
                    0x5858D0,
                    0x58D058,
                    0xD05858,
                    0x58D0D0,
                    0xD0D058,
                    0xD058D0,
                    0xA06A48,
                    0x6A48A0,
                    0x48A06A,
                    0x585858
                ],
                as_string=True
            ) for colour in c_set
        )
    }
    def get_IED_config(self):
        config = {
            'text' : MapNumbedElem.val_numbers.get(self.val),
            'fg' : MapNumbedElem.val_colours.get(self.val) if self.field.is_over else 'yellow',
            'font' : ('tkDefaultFont', 12, 'bold')
        }
        if not self.field.is_over:
            config.update(
                {
                    'bg': 'red',
                    'relief': tk.SUNKEN
                }
            )
        return config # MapNumbedElem.val_numbers.get(self.val)

    def build_surprise_box(self):
        self.box = NumbedSurprise(self)
        self.build(self.box)
        return self.box

# class MapIED(MapElem):
#     def reveal(self):
#         # if self.field.map_cleared == 0
#         if not self.revealed and not self.flagged:
#             self.create_actual()
#             self.box.destroy()
#             self.revealed = True
#             if not self.field.is_over:
#                 self.lbl.config(fg='red', text='✨')
#                 self.field.oops()
#             return self.lbl


class Surprise(tk.Button):
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        super().__init__(
            master=self.parent.frame,
            text=' ',
            fg='orange red',
            image=self.parent.field.master.empty_image,
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
    
    # def num_flag(self, num):
    #     count = self.parent.field.IED_current.get()
    #     self.config(text=str(num))
    #     self.flagged = num
    #     self.parent.field.IED_current.set(count - 1)

    def flag(self, num=None):
        if num is None:
            flag_config = {'text': '⚑'}
            num = 1
        else:
            flag_config = {
                'text': MapNumbedElem.val_numbers.get(num),
                'fg': MapNumbedElem.val_colours.get(num),
            }

        count = self.parent.field.IED_current.get()
        if self.flagged == num:
            self.config(text=' ')    #, bg='SystemButtonFace')
            self.flagged = 0
            self.parent.field.IED_current.set(count + 1)            
        else:
            self.config(**flag_config)
            if self.flagged == 0:
                self.parent.field.IED_current.set(count - 1)
            self.flagged = num

        self.parent.flagged = self.flagged
        # return self.flagged

    def check_false_flag(self):
        if not self.parent.is_IED:
            self.config(text='❌', fg='white', bg='maroon')

class NumbedSurprise(Surprise):

    # def flag(self, num):
    #     if self.flagged == num:
    #         self.config(text='')
    #         self.flagged = 0
    #     else:
    #         self.config(text=str(num))
    #         self.flagged = num
    
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

        
if __name__ == '__main__':
    gui = GUI()
    gui.run()
