# -*- coding: utf-8 -*-

##
# @file encoder.py This files contains the ME 405 encoder class.
#
# @author Ethan Czuppa
# @author Josh Anderson

import pyb

class Encoder:
    """ This class allows users to access encoder readings. It automatically
    configures the encoder based on the user-given arguments. """
    def __init__(self, pinA, pinB, af_num, tmr_num, bound=1000):
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
        """

        pinA.init(mode = pyb.Pin.AF_PP, pull = pyb.Pin.PULL_NONE, af=af_num)
        pinB.init(mode = pyb.Pin.AF_PP, pull = pyb.Pin.PULL_NONE, af=af_num)
        self._tmr = pyb.Timer(tmr_num, prescaler = 0, period = 65535)
        self._tmr.channel(1, pyb.Timer.ENC_AB)

        self._pos = 0
        self._lastcount = self._tmr.counter()
        self._bound = bound


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
        self._pos = self._pos + delta
        self._lastcount = count
        return self._pos

    def zero(self):
        """ Resets the encoder position variable to zero. """
        self._pos = 0

## SUMO Bot Left Motor
Left = Encoder(pyb.Pin.board.PC6, pyb.Pin.board.PC7, pyb.Pin.AF3_TIM8, 8)

## SUMO Bot Right Motor
Right = Encoder(pyb.Pin.board.PB6, pyb.Pin.board.PB7, pyb.Pin.AF2_TIM4, 4)
