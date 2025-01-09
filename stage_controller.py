'''
stage_controller.py

Jerome Fung (jfung@ithaca.edu)

GUI for controlling a FUYU linear stage via serial port.
'''

import tkinter as tk
from tkinter import ttk
import serial 
import platform


class StageControl(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.title("FUYU Stage Controller")

        # create widgets
        self.create_widgets()
        
    def create_widgets(self):
        rel_go_button = ttk.Button(self.parent, text = "Go").grid(column = 3,
                                                                  row = 0)
        abs_go_button = ttk.Button(self.parent, text = "Go").grid(column = 3,
                                                                  row = 1)     
        stop_button = ttk.Button(self.parent, text = "STOP").grid(column = 3,
                                                                  row = 2)


def main():
    root = tk.Tk()
    frame = StageControl(root)
    #frame.grid()
    root.mainloop()
    


if __name__ == '__main__':
    main()
