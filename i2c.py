# -*- coding: utf-8 -*-

##
# @file i2c.py
# @author Josh Anderson
# @author Ethan Czuppa
#
# Contains I2C buses for the SUMO bot

from machine import I2C
import pyb

## I2C Bus 1. Contains left time of flight sensor and accelerometer.
Bus1 = I2C(1)

## I2C Bus 2. Contains center time of flight sensor.
Bus2 = I2C(-1, pyb.Pin.board.PC3, pyb.Pin.board.PC2)

## I2C Bus 3. Contains center time of flight sensor.
Bus3 = I2C(-1, pyb.Pin.board.PC0, pyb.Pin.board.PB0)
