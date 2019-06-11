# -*- coding: utf8 -*-

import tkinter as Tk
import tkinter.ttk as ttk
from frontend.widgets import *

from Bio import SeqIO
from pyteomics.parser import expasy_rules

formats = list(iter(SeqIO._FormatToIterator))
enzymes = list(iter(expasy_rules))

class Notebook():
    """
    """
    def __init__(self, notebook, text, **kwargs):
        """
        """
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=text, **kwargs)

class UploadNotebook(Notebook):
    def __init__(self, notebook, run_function, text='Upload', **kwargs):
        """
        """
        super(UploadNotebook, self).__init__(notebook, text)

        self.input_path = Filepath(self.frame, label='Sequence File',
                                   label_grid={'row':0, 'column':0, 'sticky': 'we'},
                                    box_grid={'row': 0, 'column':1,'sticky': 'we'},
                                   button_grid={'row':0, 'column':2, 'sticky': 'we'},
                                    path_type='file')

        self.format_options = OptionBox(self.frame, label='Sequence Format', values=formats,
                                        label_grid={'row':1, 'column':0},
                                        box_grid={'row': 1, 'column':1})
        self.enzyme_options = OptionBox(self.frame, label='Enzyme', values=enzymes,
                                        label_grid={'row':2, 'column':0},
                                        box_grid={'row': 2, 'column':1},
                                        current=33)
        self.min_length = EntryBox(self.frame, label='Minimum Peptide Length',
                                   label_grid={'row':3, 'column':0},
                                   box_grid={'row': 3, 'column':1},
                                   default=5)

        self.output_path = Filepath(self.frame, label='Output Folder',
                                    label_grid={'row':4, 'column':0},
                                    box_grid={'row': 4, 'column':1},
                                    button_grid={'row':4, 'column':2},
                                    path_type='folder', optional=True)

        self.run = RunButton(self.frame, function=run_function, grid={'row': 5, 'column': 2})


class ResultsNotebook(Notebook):
    def __init__(self, notebook, no_peptides, mean_length, mean_score, pos_pred, std,
                 plot_path, file_path, text='Results', grid={}, width=75, height=7):
        """
        """
        super(ResultsNotebook, self).__init__(notebook, text)

        # setting up text summary at top of frame
        self.label = ttk.Label(self.frame, text='Summary:')
        self.summary = Tk.Text(self.frame, width=width, height=height)
        self.summary.insert('2.5','%i peptides were predicted with a mean lenght of %.2f amino acids\n%i peptides were predicted positive (%.2f%%).\nThe mean score was %.2f with a standard deviation of %.2f.'\
            %(no_peptides, mean_length, pos_pred, pos_pred/no_peptides, mean_score, std))

        self.summary.grid(row=0, column=0, stick='nwse',
                          columnspan=3)

        # setting up file path display
        self.file_path = ttk.Label(self.frame, text='Text files were saved to: %s'%file_path)
        self.file_path.grid(row=1, column=0, columnspan=2)
        self.plot_path = ttk.Label(self.frame, text='Plots were saved to: %s'%plot_path)
        self.plot_path.grid(row=2, column=0, columnspan=2)

        # showing summary plots
        self.graphics = Plots(self.frame, plot_path,
                              plot_grid={'row':3,'column':0,'columnspan':5},
                              left_button={'row':4, 'column':0},
                              right_button={'row':4, 'column':3})

def center(toplevel, size=None):
    toplevel.update_idletasks()

    screen_width = toplevel.winfo_screenwidth()
    screen_height = toplevel.winfo_screenheight()

    if size is None:
        size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))

    x = screen_width/2 - size[0]/2
    y = screen_height/2 - size[1]/2

    toplevel.geometry('+%d+%d' % (x, y))
