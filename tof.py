# -*- coding: utf-8 -*-

##
# @file tof.py
# @author Josh Anderson
# @author Ethan Czuppa
#
# Contains time of flight sensor code and sensor declaritions.

import VL53L0X
import i2c


class TOF:
    """ Time of Flight Sensor Class """

    def __init__(self, i2c):
        """ Initialize and start a TOF sensor on an i2c bus
        @param i2c Initialized I2C bus class
        """
        self.sensor = VL53L0X.VL53L0X(i2c)
        self.sensor.start()

    def read(self):
        """ Read distance in mm from sensors """
        return self.sensor.read()

## Left Time of Flight Sensor
Left = TOF(i2c.Bus1)

## Center Time of Flight Sensor
Center = TOF(i2c.Bus2)

## Right Time of Flight Sensor
Right = TOF(i2c.Bus3)
