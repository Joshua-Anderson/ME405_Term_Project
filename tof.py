import VL53L0X
import i2c


class TOF:
    def __init__(self, i2c):
        self.sensor = VL53L0X.VL53L0X(i2c)
        self.sensor.start()

    def read(self):
        return self.sensor.read()

Left = TOF(i2c.Bus1)
Center = TOF(i2c.Bus2)
Right = TOF(i2c.Bus3)
