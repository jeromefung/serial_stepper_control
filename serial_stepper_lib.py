'''
Library to send commands via serial port to Arduino controlling
a stepper motor linear stage.
'''

import serial


# configuration - FUYU FSK30J
steps_per_rev = 200
mm_per_rev = 2.0

def steps_to_mm(steps):
    return steps / steps_per_rev * mm_per_rev
    
def mm_to_steps(mm):
    return round(mm / mm_per_rev * steps_per_rev)

def initialize_serial(device):
    ser = serial.Serial(device, 9600, timeout = None, write_timeout = 10)
    return ser

def move_relative_mm(port, distance_mm):
    steps_to_move = abs(mm_to_steps(distance_mm))
    
    if distance_mm > 0:
        str_to_send = 'F' + str(steps_to_move) + '\n'
    else:
        str_to_send = 'R' + str(steps_to_move) + '\n'
    
    port.write(str_to_send.encode('utf-8'))
    # todo: read current position after move, can't block

def report_position(port):
    port.write('P\n'.encode('utf-8'))

def emergency_stop(port):
    port.write('S\n'.encode('utf-8'))
    
# reading might need to be handled by main loop of gui application
# look at serial object in_waiting
