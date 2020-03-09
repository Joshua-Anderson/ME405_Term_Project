# -*- coding: utf-8 -*-

##
# @file main.py
# @author Josh Anderson
# @author Ethan Czuppa

import pyb
import cotask
import task_share
import utime
import gc
import ir

from micropython import alloc_emergency_exception_buf
alloc_emergency_exception_buf (100)

if __name__ == '__main__':
    ir.init()

    # Task scheduler setups
    ir_task = cotask.Task(ir.handler, name = 'IR Task', priority = 1, period = 10,
                        profile = True, trace = False)
    cotask.task_list.append(ir_task)

    # Python's memory management for unused variables
    gc.collect()

    # Run the scheduler with the chosen scheduling algorithm. Quit if any
    # character is sent through the serial port
    vcp = pyb.USB_VCP()
    while not vcp.any():
        cotask.task_list.pri_sched()
    # Empty the comm port buffer of the character(s) just pressed
    vcp.read ()
    # Print a table of task data and a table of shared information data
    print ('\n' + str (cotask.task_list) + '\n')
    print (task_share.show_all())
    print (ir_task.get_trace())
    print ('\r\n')
