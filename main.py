from core.mailbox_monitor import MailboxMonitor
from sensor.sensor import HX711Sensor



def main():
    sensor = HX711Sensor()
    monitor = MailboxMonitor()
    while True:
        weight = sensor.read_weight()
        event = monitor.update(weight)
        if event:
            print(event)

if __name__ == "__main__":
    main()