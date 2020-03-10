# -*- coding: utf-8 -*-

##
# @file mpu6050.py Basic driver for the MPU6050 6-axis IMU
#
# This code was based off a MPU 6050 driver written by Lars Kellogg-Stedman
# Source can be found at https://github.com/larsks/py-mpu6050
#
# @author Ethan Czuppa
# @author Josh Anderson

class MPU6050:
    """ Basic driver for the MPU6050 6-axis IMU """

    def __init__(self, i2c, address=0x68):
        self._i2c = i2c
        self._addr = address


    def read_sensors(self):
        self.bus.readfrom_mem_into(self.address,
                                   MPU6050_RA_ACCEL_XOUT_H,
                                   self.sensors)

        data = unpack('>hhhhhhh', self.sensors)

        # apply calibration values
        return [data[i] + self.calibration[i] for i in range(7)]
