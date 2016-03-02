import Car
import json


class Temperature:

    def __init__(self, car_control, target_temp, time=None):
        if time == None:
            self.car_control = car_control
            self.target_temp = float(target_temp)
            self.response = None
            self.activate()

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





