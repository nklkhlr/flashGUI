# -*- coding: utf8 -*-

import os

import tkinter as Tk
import tkinter.ttk as ttk

from PIL import Image, ImageTk
from tkinter import filedialog as fd

class Filepath():
    """
    """
    def __init__(self, parent, label, button_text='...', label_grid={},
                 box_grid={}, button_grid={}, box_options={},
                 path_type='file', optional=False):
        """
        """
        # box label (on the left side)
        self.label = ttk.Label(parent, text=label)
        self.label.grid(**label_grid)

        if optional:
            self.optional = ttk.Label(parent, text='(optional)')
            row = self.label.grid_info()['row']
            column = self.label.grid_info()['column']
            self.optional.grid(row=int(row)+1, column=int(column))

        # box for filepath
        self.path_box = ttk.Entry(parent, **box_options)
        self.path_box.grid(**box_grid)

        # button to visually search for file
        self.button = ttk.Button(parent, text=button_text)
        self.button.grid(**button_grid)

        # binding button to askopen method
        if path_type=='file':
            self.button.config(command=lambda:self.path_box.insert(0, fd.askopenfilename()))
        else:
            self.button.config(command=lambda:self.path_box.insert(0, fd.askdirectory()))

class EntryBox():
    """
    """
    def __init__(self, parent, label, label_grid={}, box_grid={}, default=0):
        """
        """
        self.label = ttk.Label(parent, text=label)
        self.label.grid(**label_grid)

        self.box = ttk.Entry(parent)
        self.box.grid(**box_grid)

        self.box.insert(0, default)
class OptionBox():
    """
    for file format, enzmye etc.
    """
    def __init__(self, parent, label, values, label_grid={}, box_options={}, box_grid={}, current=0):
        """
        """
        self.label = ttk.Label(parent, text=label)
        self.label.grid(**label_grid)

        self.box = ttk.Combobox(parent, **box_options)
        self.box.config(values=values)
        self.box.current(current)
        self.box.grid(**box_grid)

class RunButton():
    """
    """
    def __init__(self, parent, function, label='Run', grid={}, run_with_return=True):
        """
        """
        self.button = ttk.Button(parent, text=label)
        self.button.grid(**grid)

        self.button.config(command=lambda: function())

        if run_with_return:
            parent.bind('<Return>', lambda: function())

class Progressbar():
    def __init__(self, window_label, bottom_label, wlabel_grid={'row':0, 'column':0},
                 bar_grid={'row':1, 'column':0, 'columnspan':3, 'sticky':'nwse'}):
        self.popup = Tk.Toplevel()
        self.popup.geometry('300x200')

        # top label
        ttk.Label(self.popup, text=window_label).grid(**wlabel_grid)

        #TODO: link to actual functions to properly display progress
        self.bar  = ttk.Progressbar(self.popup, mode='indeterminate')
        self.bar.grid(**bar_grid)

        # bottom label
        row = self.bar.grid_info()['row']
        column = self.bar.grid_info()['row']
        ttk.Label(self.popup, text=bottom_label).grid(row=row, column=column, sticky='nwse')

    def start(self, interval=50):
        self.bar.start(interval=interval)

    def stop(self):
        self.bar.stop()
        self.popup.destroy()

class Plots():
    def __init__(self, parent, result_path, plot_grid={}, left_button={}, right_button={}):
        hist = Image.open(os.path.join(result_path, 'score_histogram.png')).resize((700,500))
        self.hist = ImageTk.PhotoImage(hist)

        boxplot = Image.open(os.path.join(result_path, 'score_boxplot.png')).resize((700,500))
        self.boxplot = ImageTk.PhotoImage(boxplot)

        self.plot_order = [self.hist, self.boxplot]

        self.plot = ttk.Label(parent, image=self.hist)
        self.plot.grid(**plot_grid)

        self.plot_idx = 0

        self.next_button = ttk.Button(parent, text='Next')
        self.next_button.grid(**right_button)

        self.prev_button = ttk.Button(parent, text='Previous', state='disabled')
        self.prev_button.grid(**left_button)


        self.next_button.config(command=lambda: self.next())
        self.prev_button.config(command=lambda: self.previous())


    def next(self):
        """
        """
        self.plot_idx += 1

        self.plot.config(image=self.plot_order[self.plot_idx])

        # disabling or enabling buttons
        if self.plot_idx==len(self.plot_order)-1:
            self.next_button.config(state='disabled')
        if self.plot_idx==1:
            self.prev_button.config(state='normal')


    def previous(self):
        """
        """
        self.plot_idx -= 1

        self.plot.config(image=self.plot_order[self.plot_idx])

        if self.plot_idx==0:
            self.prev_button.config(state='disabled')
        if self.plot_idx==len(self.plot_order)-2:
            self.next_button.config(state='normal')
