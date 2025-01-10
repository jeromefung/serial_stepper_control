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
        
        # empty for reading from serial port 
        self.serial_buffer = b''
        
        self.current_pos_steps = 0
        
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
        
        self.rel_go_button = ttk.Button(self.parent, text = "Go", state = tk.DISABLED, 
                                        command = self.on_move_relative)
        self.rel_go_button.grid(column = 3, row = 0)
        self.abs_go_button = ttk.Button(self.parent, text = "Go", state = tk.DISABLED,
                                        command = self.on_move_absolute)
        self.abs_go_button.grid(column = 3, row = 1)     
        self.stop_button = ttk.Button(self.parent, text = "STOP", state = tk.DISABLED,
                                      command = self.on_stop)
        self.stop_button.grid(column = 3, row = 2)
                                                                      
    def on_connect_arduino(self):
        try:
            self.serial_connection = serial_stepper_lib.initialize_serial(self.serial_port_String.get())
            self.serial_connected = True
            for button in [self.rel_go_button, self.abs_go_button, self.stop_button]:
                button.config(state = tk.NORMAL)
                
        except (FileNotFoundError, serial.SerialException):
            tk.messagebox.showerror(title='Error', message = 'Could not connect to Arduino. Try another serial port.')

    def on_move_relative(self):
        # validate the entry 
        relative_pos = self.relative_pos_String.get()
        #print(relative_pos)
        if self.validate_position(relative_pos): # ok
            serial_stepper_lib.move_relative_mm(self.serial_connection, float(relative_pos))

    def on_move_absolute(self):
        # validate
        absolute_pos = self.absolute_pos_String.get()
        if self.validate_position(absolute_pos):
            delta = float(absolute_pos) - serial_stepper_lib.steps_to_mm(self.current_pos_steps)
            serial_stepper_lib.move_relative_mm(self.serial_connection, delta)
        
    def on_stop(self):
        serial_stepper_lib.emergency_stop(self.serial_connection)
        serial_stepper_lib.report_position(self.serial_connection)


    def validate_position(self, value_as_str):
        try:
            num = float(value_as_str)
            # check if entry has a decimal point, and if so no more than 2 decmial places
            if '.' in value_as_str:
                decimals = value_as_str.split('.')[1]
                if len(decimals) > 2:
                    tk.messagebox.showerror(title = 'Error', 
                                            message = 'Too many decimal places (no more than 2).')
                    return False
                
            return True
        except ValueError: # conversion to float failed
            tk.messagebox.showerror(title = 'Error',
                                    message = 'Invalid entry (must be integer or float with at most 2 decimal places).')
            return False
            

    def check_position_update(self):
        if self.serial_connected:
            if self.serial_connection.in_waiting > 0:
                self.serial_buffer = self.serial_buffer + self.serial_connection.read(self.serial_connection.in_waiting)
                # see if we got a complete message from serial ending in \r\n, keep listening otherwise
                #print(self.serial_buffer)
                if self.serial_buffer.decode()[-2:] == '\r\n':
                    position_in_steps = self.serial_buffer.decode().split('\r\n')[-2]
                    # if there were multiple communications, take the most recent one 
                    self.serial_buffer = b'' # clear it
                    self.current_pos_steps = int(position_in_steps)
                    # convert from steps to float
                    position_in_mm = serial_stepper_lib.steps_to_mm(self.current_pos_steps)
                    self.current_pos_String.set(str(position_in_mm))
                    
        self.after(100, self.check_position_update)
            

def main():
    root = tk.Tk()
    frame = StageControl(root)
    root.after(100, frame.check_position_update)
    root.mainloop()
    


if __name__ == '__main__':
    main()
