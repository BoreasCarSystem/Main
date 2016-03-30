import Car
import json
from threading import Thread
from time import sleep

TIME_LIMIT = 15

class Temperature(Thread):

    def __init__(self, car_control, main, target_temp, time=None):
        super(Temperature, self).__init__()
        self.main = main
        self.car_control = car_control
        self.target_temp = float(target_temp)
        self.response = None
        self.time = time
        self.start()

    def run(self):
        if self.time is None:
            self.activate()

        else:
            # TODO: Make sure time is converted to seconds at some point, and that it is TIME_LIMIT before set time.
            sleep(self.time)
            self.activate()

    def activate(self):
        # Tells CarControl to activate the AC to the given target_temp.
        # Format to be sent:
        # { "enable": true, "temperature": target_temp }

        di = {"enabled": True, "temperature": self.target_temp}
        data = json.dumps(di)
        self.response = self.car_control.set_AC(data)
        sleep(TIME_LIMIT)
        self.deactivate()

    def deactivate(self, err=None):
        # Tells CarControl to deactivate AC
        # Can be called from batteryListener or main
        # An error message (code 6 or 7) should be sent from BatteryListener to Main if BatteryListener calls
        # deactivate.
        # An ok-message should be sent from main to web server if main is the source (then it is likely that the user
        # has canceled the AC). This can be sent via the CarControl-class.

        di = {"enabled": False, "temperature": None}
        data = json.dumps(di)
        self.response = self.car_control.set_AC(data)
        if err is not None:
            self.main.add_error_message(err, "")

    def update_temperature(self, target_temp):
        self.target_temp = target_temp
        self.activate()


