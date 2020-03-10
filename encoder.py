# -*- coding: utf-8 -*-

##
# @file encoder.py This files contains the ME 405 encoder class.
#
# @author Ethan Czuppa
# @author Josh Anderson

import pyb
import utime

## This is specific to our SUMO bot with 2 in diameter wheels and specific encoder ticks/rev
INCHES_PER_TICK = 0.0064

## This is specific to our SUMO bot with 2 in diameter wheels and specific encoder ticks/rev
# Assumming the bot is spinning in place
DEG_PER_TICK = 0.1

class Encoder:
    """ This class allows users to access encoder readings. It automatically
    configures the encoder based on the user-given arguments. """
    def __init__(self, pinA, pinB, af_num, tmr_num, bound=1000, invert=False):
        """ Sets up the user desired timer and pin for a quadature encoder scheme
        with a 16 bit counter.

        @param pinA encoder channel A pin
        @param pinB encoder channel B pin
        @param af_num desired alternate function for encoder pins
        @param tmr_num desired timer
        @param bound when reading the encoder, this is the bound within the encoder min/max
         that wrapping will be assumed.
         The larger the value, the more slowly the encoder can be polled,
         but it's more likely the motor moving at fast speed would be mistaken
         for the encoder value wrapping around its max value.
         See mainpage limitations section for more details
        @param invert invert the encoders direction
        """

        pinA.init(mode = pyb.Pin.AF_PP, pull = pyb.Pin.PULL_NONE, af=af_num)
        pinB.init(mode = pyb.Pin.AF_PP, pull = pyb.Pin.PULL_NONE, af=af_num)
        self._tmr = pyb.Timer(tmr_num, prescaler = 0, period = 65535)
        self._tmr.channel(1, pyb.Timer.ENC_AB)

        self._pos = 0
        self._lastcount = self._tmr.counter()
        self._bound = bound
        self._invert = invert


    def read(self):
        """ Returns the current postion of the motor as an encoder count
        and handles timer overflows and underflows.

        @return returns the current position of the motor (encoder count) """
        timer_max = 65535

        count = self._tmr.counter()

        if self._lastcount > timer_max - self._bound and count < self._bound:
            delta = (timer_max - self._lastcount + count)
        elif count > timer_max - self._bound  and self._lastcount < self._bound:
            delta = -1*(timer_max - count + self._lastcount)
        else:
            delta = count - self._lastcount

        if self._invert:
            delta *= -1
        self._pos = self._pos + delta
        self._lastcount = count
        return self._pos

    def zero(self):
        """ Resets the encoder position variable to zero. """
        self._pos = 0

class EncoderState:
    def __init__(self, ticks, time_ms, vel_ticks, dt):
        self.ticks = ticks
        self.time_ms = time_ms
        self.vel_ticks_ms = vel_ticks
        self.dt = dt

LastLState = EncoderState(0, 0, 0, 0)
LastRState = EncoderState(0, 0, 0, 0)

def read():
    """ Task used to read encoders """
    global LastLState
    global LastRState

    now = utime.ticks_ms()
    dt = utime.ticks_diff(now, LastLState.time_ms)

    # Avoid noise from small timesteps with small tick changes
    if dt < 2:
        return LastLState, LastLState

    l_ticks = Left.read()
    r_ticks = Right.read()
    LState = EncoderState(l_ticks, now, (l_ticks-LastLState.ticks)/dt, dt)
    RState = EncoderState(r_ticks, now, (r_ticks-LastRState.ticks)/dt, dt)

    LastLState = LState
    LastRState = RState

    return LState, RState

def ticks_to_in(ticks):
    """ Convert from encoder ticks to inches

    @param ticks encoder ticks"""

    return ticks*INCHES_PER_TICK

def in_to_ticks(inches):
    """ Convert from inches to encoder ticks

    @param inches distance in inches"""
    return inches/INCHES_PER_TICK

def ticks_to_deg(ticks):
    """ Assuming bot is spinning in place, encoder ticks to degrees rotation

    @param ticks encoder ticks"""

    return ticks*DEG_PER_TICK

def deg_to_ticks(deg):
    """  Assuming bot is spinning in place, degree rotation to encoder ticks

    @param deg angle"""
    return deg/DEG_PER_TICK

## SUMO Bot Left Motor
Left = Encoder(pyb.Pin.board.PC6, pyb.Pin.board.PC7, pyb.Pin.AF3_TIM8, 8)

## SUMO Bot Right Motor
Right = Encoder(pyb.Pin.board.PB6, pyb.Pin.board.PB7, pyb.Pin.AF2_TIM4, 4, invert=True)
