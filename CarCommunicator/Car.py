""" We're pretending that this class is a real car.
In the real world, this might be a set of circuits or something."""

import json

class CarControl():

    def __init__(self):
        self.AC_enabled = False
        self.AC_target_temperature = None

    def set_AC(self, data):
        di = json.loads(data)

        if type(di["enabled"]) == bool and (type(di["temperature"]) == float or di["temperature"] is None):
            self.AC_enabled = di["enabled"]
            self.AC_target_temperature = di["temperature"]
            return "200 ok"
        else:
            return "Invalid data"