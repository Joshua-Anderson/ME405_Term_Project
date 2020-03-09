from machine import I2C
import pyb

Bus1 = I2C(1)
Bus2 = I2C(-1, pyb.Pin.board.PC3, pyb.Pin.board.PC2)
Bus3 = I2C(-1, pyb.Pin.board.PC0, pyb.Pin.board.PB0)
