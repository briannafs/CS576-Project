from .sensor import HX711Sensor

def calibrate(sensor):
    sensor.tare()
    input("Place known weight, then press Enter...")
    reading = sensor.read_weight()
    known = float(input("Enter weight: "))
    ratio = reading / known
    sensor.set_scale(ratio)
    return ratio