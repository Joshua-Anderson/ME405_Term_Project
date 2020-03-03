# -*- coding: utf-8 -*-

##
# @file motor_driver.py This file contains code for pwm based motor driving
#
# @author Josh Anderson
# @author Ethan Czuppa

import pyb

class MotorDriver:
    """ This class implements a PWM motor driver """
    def __init__ (self, pin_en, pin_a, pin_b, tmr_num):
        """ Creates a motor driver by initializing GPIOpins
        and turning the motor off for safety.

        @param pin_en pin used to enable motor controller
        @param pin_a positive motor pin
        @param pin_b negative motor pin
        @param tmr_num timer number used to drive motor.
               Must be compatible with chosen pins """

        pin_en.init(pyb.Pin.OUT_PP)
        pin_a.init(pyb.Pin.OUT_PP)
        pin_b.init(pyb.Pin.OUT_PP)

        # Enables motor controller channel
        pin_en.high()

        # Initializes Timer and sets and sets PWM pulse width
        tmr = pyb.Timer(tmr_num, freq=20000)
        self._tmr_ch1 = tmr.channel(1, pyb.Timer.PWM, pin=pin_a)
        self._tmr_ch1.pulse_width_percent (0)
        self._tmr_ch2 = tmr.channel(2, pyb.Timer.PWM, pin=pin_b)
        self._tmr_ch2.pulse_width_percent(0)

    def set_duty_cycle (self, level):
        """ This method sets the duty cycle to be sent
        to the motor to the given level. Positive values
        cause torque in one direction, negative values
        in the opposite direction.

        @param level A signed integer holding the duty
        cycle of the voltage sent to the motor """

        # Appropriately sets PWM pulse width based on inputted level parameter
        if level < 0:
            self._tmr_ch1.pulse_width_percent(abs(level))
            self._tmr_ch2.pulse_width_percent(0)
        else:
            self._tmr_ch1.pulse_width_percent(0)
            self._tmr_ch2.pulse_width_percent(level)

## SUMO Bot Left Motor
Left = MotorDriver(pyb.Pin.board.PA10, pyb.Pin.board.PB4, pyb.Pin.board.PB5, 3)

## SUMO Bot Right Motor
Right = MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1, 5)
