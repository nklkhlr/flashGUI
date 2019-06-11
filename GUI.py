# -*- coding: utf8 -*-

# for reference Desktop/Python/GUI/lipidomics_gui.py

import tkinter as Tk
from backend.FlashScore import flashScore

from frontend.frames import *

class FlashApp():
    def __init__(self, master):
        self.master = master
        self.master.title('Flash Score')

        self.notebook = ttk.Notebook(self.master)
        self.notebook.grid(sticky='nwse')
        Tk.Grid.columnconfigure(self.notebook, 0, weight=1)
        Tk.Grid.rowconfigure(self.notebook, 0, weight=1)

        self.upload = UploadNotebook(notebook=self.notebook,
                                     run_function=self.run_prediction_)

    def run_prediction_(self):
        # TODO: progressbar and main calculation in different threads
        ## set up progressbar
        #progressbar = Progressbar(window_label='', bottom_label='Predicting...')
        #center(progressbar.popup)
        #progressbar.start()

        Flash = flashScore(self.upload.input_path.path_box.get(),
                           seqFormat=self.upload.format_options.box.get(),
                           enzyme=self.upload.enzyme_options.box.get(),
                           min_length=int(self.upload.min_length.box.get()))
        Flash.predictScore()
        Flash.stats()
        Flash.visualizeStats(path=self.upload.output_path.path_box.get())
        Flash.writeResults(path=self.upload.output_path.path_box.get())

        self.results = ResultsNotebook(self.notebook, no_peptides=Flash.stats['No. of Peptides'],
                                       mean_length=Flash.stats['Mean length'],
                                       mean_score=Flash.stats['Mean score'],
                                       pos_pred=sum(Flash.predictions),
                                       std=Flash.stats['Std. score'],
                                       plot_path=Flash.plot_path,
                                       file_path=Flash.file_path)

        #progressbar.stop()

        self.notebook.select(self.results.frame)

        self.master.geometry('750x750')
        center(self.master)


def main():

    FONTT = ('Helvetica', '12')

    root = Tk.Tk()
    Tk.Grid.columnconfigure(root, 0, weight=1)
    Tk.Grid.rowconfigure(root, 0, weight=1)

    root.geometry('700x500')
    center(root)
    root.resizable(True,True)

    app = FlashApp(root)

    root.mainloop()

main()
