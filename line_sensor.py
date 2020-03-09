"""
@file line_sensor.py This file contains the line sensor driver class for the ME 405 term project
@author: Josh Anderson
@author: Ethan Czuppa
"""

import pyb
import utime

RS_T = 10    # rise time to let pulse rise after being driven high in microseconds
SLP_T = 1000   # sleep time waiting for pulse to decay in microseconds

class LineSense:
    """
    This class implements a line sensor driver for the ME 405 Nucleo dev board
    specifically for the SUMO bot
    """
    def __init__(self,pin_sig,pin_config):
        """
        Configures the line sensing signal pins to be read and timed
        @param pin_sig the I/O pin on the Nucleo breakout (shoe) for the line sensor
        @param pin_config initially configured to output to drive signal pins high
        """
        self.pin_sig = pin_sig


    def read(self):
        """
        Toggles pin mode between output being driven high and input waiting to go low
        while simultaneously measuring the lenght of the pulse decay to determine if
        the surface is white or black. Returns the line boolean that tells the supervisor
        task if an edge has/has not been detected
        """
        self.pin_sig.init(pyb.Pin.OUT_PP)
        self.pin_sig.high()
        utime.sleep_us(RS_T)
        self.pin_sig.init(pyb.Pin.IN)
        utime.sleep_us(SLP_T)
        if not self.pin_sig.value():
            return True
        return False


## Sumo Bot Line Sensors
fr = LineSense(pyb.Pin.board.PA4, pyb.Pin.OUT_PP)
fl = LineSense(pyb.Pin.board.PC4, pyb.Pin.OUT_PP)
br = LineSense(pyb.Pin.board.PA3, pyb.Pin.OUT_PP)
bl = LineSense(pyb.Pin.board.PA5, pyb.Pin.OUT_PP)