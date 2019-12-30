from random import sample, randrange
from collections import namedtuple
from tkinter import messagebox, font
from time import time

import tkinter as tk

# This feels kinda useless to be honest, probably will remove.
Dimension = namedtuple('Dimension', 'x y')

# Mouse state constants
MOUSE_LEFT = 2 ** 8
MOUSE_MID = 2 ** 9
MOUSE_RIGHT = 2 ** 10
OKAY = '☺'
DEAD = '☠'
YEAH = '✌'

MODE = {
    0: {'dimension': Dimension(9, 9), 'amount': 10},
    1: {'dimension': Dimension(16, 16), 'amount': 40},
    2: {'dimension': Dimension(30, 16), 'amount': 99}
}

def prod(iterable):
    result = 1
    for x in iterable:
        result *= x
    return result

class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        # default_font = font.nametofont('TkDefaultFont')
        # default_font.configure(size=8)
        self.title('PyMS')
        self.menubar = tk.Menu(self)
        self.var_mode = tk.IntVar()
        self.var_mode.set(2)
        diff_menu = tk.Menu(self, tearoff=0)
        for i, mode in enumerate(('Noob', 'Skilled', 'Pro')):
            diff_menu.add_radiobutton(
                label=mode,
                value=i,
                variable=self.var_mode,
                command=lambda x=i: self.build_field(**MODE.get(x))
            )
        # diff_menu.add_radiobutton(label='Noob', command=lambda: self.build_field(**MODE.get(1)))
        # diff_menu.add_radiobutton(label='Skilled', command=lambda: self.build_field(**MODE.get(2)))
        # diff_menu.add_radiobutton(label='Pro', command=lambda: self.build_field(**MODE.get(3)))
        self.menubar.add_cascade(label='Mode', menu=diff_menu)
        self.config(menu=self.menubar)
        self.face = tk.StringVar()
        self.face.set(OKAY)
        self.timer = Timer(self)
        self.field = None
        self.build_status_bar()

    def build_status_bar(self):
        self.frm_status = tk.Frame(self) #, height=48)
        self.frm_timer = tk.LabelFrame(self.frm_status, text='Time:')
        self.lbl_timer = tk.Label(self.frm_timer, textvariable=self.timer.string)
        self.btn_main = tk.Button(
            self.frm_status,
            textvariable=self.face,
            command=lambda: self.build_field(**MODE.get(self.var_mode.get())),
            font=('tkDefaultFont', 18),
            bg='yellow',
            anchor=tk.N
        )
        self.frm_IEDs = tk.LabelFrame(self.frm_status, text='IEDs:')
        self.lbl_IEDs = tk.Label(self.frm_IEDs, text='0')
        
        # self.frm_status.grid_propagate(False)
        self.frm_status.pack(fill=tk.BOTH, expand=True)
        self.frm_status.columnconfigure(index=0, weight=3)
        self.frm_status.columnconfigure(index=1, weight=1)
        self.frm_status.columnconfigure(index=2, weight=3)
        self.frm_timer.grid(row=0, column=0, sticky=tk.NSEW)
        self.btn_main.grid(row=0, column=1, sticky=tk.N)
        self.frm_IEDs.grid(row=0, column=2, sticky=tk.NSEW)
        self.lbl_timer.pack()
        self.lbl_IEDs.pack()

    def build_field(self, *args, **kwargs):
        if not self.field is None:
            self.field.destroy()
        self.field = Field(self, *args, **kwargs)
        self.field.build()
        # self.var_timer.set(0)
        self.lbl_IEDs.config(textvariable=self.field.IED_current)
        self.face.set(OKAY)
        self.timer.start()

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
        self._job = self.master.after(ms=1000, func=self._update)

    def to_string(self, val=None):
        if val:
            current = val
        else:
            current = time() - self.start_time
        h, m, s = int(current // 360), int(current % 360 // 60), int(current % 60)
        self.string.set(f'{h:02}:{m:02}:{s:02}')
    
    def stop(self):
        self.end_time = time() - self.start_time
        self.to_string()
        self.master.after_cancel(self._job)
        return self.end_time


class Field:
    def __init__(self, master:tk.Toplevel, dimension:Dimension=Dimension(16, 16), rate:float=.15, amount=40):
        self.master = master
        self.dimension = dimension
        self.frame = tk.Frame(master=self.master)
        self.empty_image = tk.PhotoImage(width=1, height=1)
        self.is_over = False
        if amount:
            self.IED_count = amount
        else:
            self.IED_count = int(prod(dimension) * rate)
        self.IED_current = tk.IntVar()
        self.IED_current.set(self.IED_count)
        self.IEDs = self.set_IEDs()
        self.map_cleared = 0
        self.map_goal = dimension.x * dimension.y - self.IED_count
        # self.map = self.create_map()
        self.map = {
            (x, y): MapIED(self, (x, y), 1) if (x, y) in self.IEDs else MapElem(self, (x, y))
            #MapElem(self, (x, y), 'X' if (x, y) in self.IEDs else None)
            for x in range(dimension.x)
            for y in range(dimension.y)
        }
        # self.map = FieldMap(self.frame, dimension, self.IEDs)
        # self.cells = {
        #     (x, y): Surprise(coord=(x, y), elem=self.map.get((x, y)) master=self.frame, width=3) 
        #     for x in range(dimension.x)
        #     for y in range(dimension.y)
        # }
        # self.IEDs = sample(self.cells.keys(), self.IED_count) 
        # for IED in self.IEDs:
        #     self.cells[IED].is_IED = True

    def build(self):
        # for (x, y) in self.cells.keys():
        #     lbl = tk.Label(self.frame, text='X' if (x, y) in self.IEDs else '')
        #     lbl.grid(row=y, column=x, sticky=tk.NSEW)
        #     lbl.lower()
        # self.map.fill()
        # for coord, cell in self.cells.items():
        #     build(cell, coord)
        for elem in self.map.values():
            elem.build_surprise_box()
        self.frame.pack_propagate(False)
        self.frame.pack()

    def set_IEDs(self):
        IEDs = set()
        while len(IEDs) < self.IED_count:
            IEDs.add(
                (randrange(self.dimension.x), randrange(self.dimension.y))
            )
        return IEDs

    def oops(self):
        self.master.timer.stop()
        self.master.face.set(DEAD)
        self.is_over = True
        for IED in self.IEDs:
            self.map.get(IED).reveal()
        messagebox.showwarning("It's over Anakin!", 'I have the highground.')

    def check_clear(self):
        self.map_cleared += 1
        if self.map_cleared >= self.map_goal:
            self.master.timer.stop()
            self.master.face.set(YEAH)
            self.is_over = True
            messagebox.showinfo("It's wonderful!", 'You did it!')


    # def create_map(self):
    #     field_map = dict()
    #     def count_IED(coord):
    #         nonlocal field_map
    #         cx, cy = coord
    #         # count = sum(adj == 'X' for adj in adjacents)
    #         count = sum(field_map.get((rx, ry)) == 'X' for rx in range(cx-1, cx+2) for ry in range(cy-1, cy+2))
    #         # colour = FieldMap.clue_colours.get(count, 'SystemButtonText')
    #         return count    # MapElem(self.frame, coord, count)
    
    #     for coord in self.IEDs:
    #         field_map[coord] = MapElem(self, coord, 'X')
    #     for x in range(self.dimension.x):
    #         for y in range(self.dimension.y):
    #             # adjacents = [field_map.get((rx, ry)) for rx in range(cx-1, cx+2) for ry in range(cy-1, cy+2) if field_map.get((rx, ry))]
    #             field_map.setdefault(
    #                 (x, y), 
    #                 MapElem(
    #                     self,
    #                     (x, y),
    #                     count_IED((x, y))
    #                 )
    #             )
    #     return field_map
    
    def destroy(self):
        self.frame.destroy()


# class FieldMap:
    
#     # Inner class to build the map with numbers
#     def __init__(self, master:tk.Toplevel, dimension:Dimension, IEDs:list):
#         self.master = master
#         self.dimension = dimension




#     def get(self, coord):
#         return self.map.get(coord)

    
#     def fill(self):
#         for coord, elem in self.map.items():
#             lbl = tk.Label(self.master, text=str(elem.val) if elem.val else '', fg=elem.colour)
#             build(lbl, coord)
#             lbl.lower()

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
        self.is_IED = True if val else False
        self.clue = None
        self.flagged = False
        self.revealed = False
        self.box = None
        self.lbl = None

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

    def reveal(self):
        if not self.revealed and not self.flagged:
            if not self.is_IED:
                self.count_adjacent_IEDs()
            self.lbl = tk.Label(
                master=self.frame,
                text='✹' if self.val else self.clue if self.clue else '',
                fg=MapElem.clue_colours.get(self.clue, 'SystemButtonText')
            )
            self.lbl.bind('<ButtonRelease-1>', self._click)
            self.lbl.bind('<ButtonRelease-3>', self._click)
            self.box.destroy()
            self.build(self.lbl)
            self.revealed = True
            if self.clue == 0:
                for elem in self.adjacents():
                    elem.reveal()
            if not self.field.is_over:
                if self.is_IED:
                    self.lbl.config(fg='red')
                    self.field.oops()
                else:
                    self.field.check_clear()
            return self.lbl

    def __eq__(self, other):
        return self.val == other

    def _click(self, evt):
        if self.field.is_over:
            return
        w, h = evt.widget.winfo_geometry().replace('+', 'x').split('x')[:2]
        if evt.x in range(int(w)) and evt.y in range(int(h)):
            if (evt.num == 1 and evt.state & MOUSE_RIGHT) or (evt.num == 3 and evt.state & MOUSE_LEFT):
                self.both_release()
            elif evt.num == 1:
                self.left_release(evt.state)
            elif evt.num == 3:
                self.right_release(evt.state)

    def left_release(self, mods=None):
        self.reveal()
        # tk.Label(self.master, text='X' if self.is_IED else 'O').grid(row=self.y, column=self.x, sticky=tk.NSEW)

            # for elem in self.field.map.values():
            #     if elem.is_IED:
            #         elem.reveal()
            #     elif not elem.revealed:
            #         print(elem.coord)
            #         elem.box.config(state=tk.DISABLED)
            # messagebox.showwarning('Uh oh...', 'Boom!')
            # self.frame.config(state=tk.DISABLED)
    
    def right_release(self, mods=None):
        if not self.revealed:
            self.flagged = self.box.flag()
        # if mods & MOUSE_LEFT:
        #     self.reveal()
        #     for adj in self.adjacents():
        #         adj.reveal()

    def both_release(self, *evt):
        adjs = list(self.adjacents())
        flags = sum(adj.flagged for adj in adjs)
        if flags == self.clue:
            self.reveal()
            for adj in adjs:
                adj.reveal()
        else:
            self.field.master.bell()

class MapIED(MapElem):
    pass


class Surprise(tk.Button):
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        super().__init__(
            master=parent.frame,
            fg='red',
            image=parent.field.empty_image,
            width=20, height=20,
            compound='c',
            relief=tk.GROOVE,
            *args, **kwargs
        )
        self.flagged = False
        self.bind('<ButtonRelease-1>', parent._click)
        self.bind('<ButtonRelease-3>', parent._click)
    
    def flag(self):
        count = self.parent.field.IED_current.get()
        if self.flagged:
            self.config(text='')    #, bg='SystemButtonFace')
            self.flagged = False
            self.parent.field.IED_current.set(count + 1)
        else:
            self.config(text='⚑')
            self.flagged = True
            self.parent.field.IED_current.set(count - 1)
        return self.flagged

        
if __name__ == '__main__':
    gui = GUI()
    gui.run()
