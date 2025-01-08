'''
Library to send commands via serial port to Arduino controlling
a stepper motor linear stage.
'''

import serial


# configuration - FUYU FSK30J
steps_per_rev = 200
mm_per_rev = 2.0

def initialize_serial():
    ser = serial.SerialPort(9600, timeout = None, write_timeout = 10)
    

def move_relative_mm(distance_mm):
    steps_to_move = round(abs(distance_mm) / mm_per_rev * steps_per_rev)
    
    if distance > 0:
        str_to_send = 'F' + str(steps_to_move) + '\n'
    else:
        str_to_send = 'R' + str(steps_to_move) + '\n'
    
    ser.write(str_to_send.encode('utf-8'))
    # todo: read current position after move, can't block

def emergency_stop():
    ser.write('S\n'.encode('utf-8'))
    
