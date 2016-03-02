import Car
import json


class Temperature:

    def __init__(self, target_temp, time=None):
        if time == None:
            self.car_control = Car.CarControl()
            self.target_temp = float(target_temp)
            self.response = None
            self.activate()
            self.send_response()

    def activate(self):
        # Tells CarControl to activate the AC to the given target_temp.
        # Format to be sent:
        # { "enable": true, "temperature": target_temp }

        dict = {"enabled": True, "temperature": self.target_temp}
        data = json.dumps(dict)
        self.response = self.car_control.set_AC(data)


    def deactivate(self, error_no=None):
        dict = {"enabled": False, "temperature": None}
        data = json.dumps(dict)
        self.response = self.car_control.set_AC(data)

        if error_no is None:
            # If the web server has canceled the AC.
        else:
            # Do something with

    def get_response(self):
