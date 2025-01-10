'''
stage_controller.py

Jerome Fung (jfung@ithaca.edu)

GUI for controlling a FUYU linear stage via serial port.
'''

import tkinter as tk
import tkinter.messagebox
from tkinter import ttk
import serial 
import serial.tools.list_ports
import platform
import serial_stepper_lib


class StageControl(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.title("FUYU Stage Controller")

        # Find available serial ports 
        self.ports_list = [port.device for port in serial.tools.list_ports.comports()]
        self.serial_connected = False # flag variable
        
        # create widgets
        self.create_widgets()
        
        # adjust layout
        self.parent.rowconfigure(0, pad = 5)
        self.parent.rowconfigure(1, pad = 5)
        self.parent.rowconfigure(2, pad = 20)
        self.parent.columnconfigure(0, pad = 80)
        self.parent.columnconfigure(3, pad = 20)
        
    def create_widgets(self):
        ttk.Label(self.parent, text = "Select Arduino serial port:").grid(column = 0, row = 0, sticky = tk.W, padx = 5)
        self.serial_port_String = tk.StringVar()
        self.port_select_combobox = ttk.Combobox(self.parent, textvariable = self.serial_port_String,
                                                 state = 'readonly',
                                                 values = self.ports_list).grid(column = 0, row = 1, sticky = tk.W, padx = 5)
        self.connect_button = ttk.Button(self.parent, text = "Connect Arduino",
                                         command = self.on_connect_arduino)
        self.connect_button.grid(column = 0, row = 2, sticky = tk.W, padx = 5)

        ttk.Label(self.parent, text = "Move relative to current position [mm]:").grid(column = 1, row = 0, sticky = tk.W)
        ttk.Label(self.parent, text = "Move to absolute position [mm]:").grid(column = 1, row = 1, sticky = tk.W)
        
        self.relative_pos_String = tk.StringVar()
        self.relative_pos_entry = ttk.Entry(self.parent,
                                            textvariable = self.relative_pos_String,
                                            width = 12)
        self.relative_pos_entry.grid(column = 2, row = 0)
                                            
        self.absolute_pos_String = tk.StringVar()
        self.absolute_pos_entry = ttk.Entry(self.parent,
                                            textvariable = self.absolute_pos_String,
                                            width = 12)
        self.absolute_pos_entry.grid(column = 2, row = 1)
                                            
        self.current_pos_frame = ttk.LabelFrame(self.parent, 
                                                borderwidth = 5, relief = tk.RIDGE).grid(column = 1, row = 2, columnspan = 2)                                    
        
        self.current_pos_String = tk.StringVar()
        self.current_pos_String.set('0.00')                                    
        
        ttk.Label(self.current_pos_frame, text = "Current position [mm]:").grid(column = 1, row = 2)
        self.current_pos_label = ttk.Label(self.current_pos_frame, 
                                           textvariable = self.current_pos_String).grid(column = 2, row = 2)
        
        self.rel_go_button = ttk.Button(self.parent, text = "Go", state = tk.DISABLED)
        self.rel_go_button.grid(column = 3, row = 0)
        self.abs_go_button = ttk.Button(self.parent, text = "Go", state = tk.DISABLED)
        self.abs_go_button.grid(column = 3, row = 1)     
        self.stop_button = ttk.Button(self.parent, text = "STOP", state = tk.DISABLED)
        self.stop_button.grid(column = 3, row = 2)
                                                                      
    def on_connect_arduino(self):
        try:
            self.serial_connection = serial_stepper_lib.initialize_serial(self.serial_port_String.get())
            self.serial_connected = True
            for button in [self.rel_go_button, self.abs_go_button, self.stop_button]:
                button.state = tk.NORMAL
                
        except (FileNotFoundError, serial.SerialException):
            tk.messagebox.showerror(title='Error', message = 'Could not connect to Arduino. Try another serial port.')


def main():
    root = tk.Tk()
    frame = StageControl(root)
    #frame.grid()
    root.mainloop()
    


if __name__ == '__main__':
    main()
