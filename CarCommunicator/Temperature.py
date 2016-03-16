import Car
import json
from threading import Thread
from time import sleep


class Temperature(Thread):

    def __init__(self, car_control, target_temp, time=None):
        super(Temperature, self).__init__()
        self.car_control = car_control
        self.target_temp = float(target_temp)
        self.response = None
        if time is None:
            self.activate()
        else:
            # TODO: Make sure time is converted to seconds at some point
            timer = TemperatureTimer(time, self)
            timer.start()


    def activate(self):
        # Tells CarControl to activate the AC to the given target_temp.
        # Format to be sent:
        # { "enable": true, "temperature": target_temp }

        di = {"enabled": True, "temperature": self.target_temp}
        data = json.dumps(di)
        self.response = self.car_control.set_AC(data)

    def deactivate(self):
        # Tells CarControl to deactivate AC
        # Can be called from batteryListener or main
        # An error message (code 6 or 7) should be sent from BatteryListener to Main if BatteryListener calls
        # deactivate.
        # An ok-message should be sent from main to web server if main is the source (then it is likely that the user
        # has canceled the AC). This can be sent via the CarControl-class.

        di = {"enabled": False, "temperature": None}
        data = json.dumps(di)
        self.response = self.car_control.set_AC(data)

    def update_temperature(self, target_temp):
        self.target_temp = target_temp
        self.activate()


class TemperatureTimer(Thread):
    def __init__(self, delay, temperature):
        super(TemperatureTimer, self).__init__()
        self.delay = delay
        self.temperature = temperature

    def run(self):
        sleep(self.delay)
        self.temperature.activate()
