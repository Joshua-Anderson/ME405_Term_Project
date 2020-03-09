import VL53L0X
from machine import I2C


class TOF:
    def __init__(self, i2c):
        self.sensor = VL53L0X.VL53L0X(i2c)
        self.sensor.start()

    def read(self):
        return self.sensor.read()

Left = TOF()
