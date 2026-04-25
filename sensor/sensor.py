
import RPi.GPIO as GPIO  
from hx711 import HX711  

class HX711Sensor:
    def __init__(self, dout_pin=21, pd_sck_pin=20):
        self.hx = HX711(dout_pin=dout_pin, pd_sck_pin=pd_sck_pin)

    def tare(self):
        err = self.hx.zero()
        if err:
            raise ValueError("Tare failed")

    def set_scale(self, ratio):
        self.hx.set_scale_ratio(ratio)

    def read_weight(self):
        return self.hx.get_weight_mean(20)