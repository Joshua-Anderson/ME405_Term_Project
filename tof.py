# -*- coding: utf-8 -*-

##
# @file tof.py
# @author Josh Anderson
# @author Ethan Czuppa
#
# Contains time of flight sensor code and sensor declaritions.

import VL53L0X
import i2c
import utime


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
        val = self.sensor.read()
        if val > 2000:
            val = 0
        return val

TofAng = None
TofLastRead = 0

def read():
    global TofAng
    global TofLastRead

    now = utime.ticks_ms()
    dt = now - TofLastRead

    # Only return new value every 40 Ms
    if dt < 100:
        return TofAng

    l = Left.read()
    c = Center.read()
    r = Right.read()
    sum = l + c + r

    TofLastRead = now

    if sum == 0:
        TofAng = None
        return None

    TofAng = -20*(l/sum) + 20*(r/sum)
    return TofAng

def ang_to_vec(deg):
    if deg is None:
        return None
    return deg/20.0


## Left Time of Flight Sensor
Left = TOF(i2c.Bus1)

## Center Time of Flight Sensor
Center = TOF(i2c.Bus2)

## Right Time of Flight Sensor
Right = TOF(i2c.Bus3)
