""" We're pretending that this class is a real car.
In the real world, this might be a set of circuits or something."""

import json

DEBUG = True

class CarControl:
    def __init__(self):
        self.AC_enabled = False
        self.AC_target_temperature = None

    def set_AC(self, data):
        di = json.loads(data)
        changed = False
        if "enabled" in di and type(di["enabled"]) == bool:
            self.AC_enabled = di["enabled"]
            changed = True
        if "temperature" in di and (type(di["temperature"]) == float):
            self.AC_target_temperature = di["temperature"]
            changed = True
        print("Car AC has changed status: ", self.AC_enabled, self.AC_target_temperature)
        return changed
