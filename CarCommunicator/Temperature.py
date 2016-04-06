import Car
import json
from threading import Thread, Lock
from time import sleep
import datetime

AC_NOT_START_LIMIT = 25
AC_ABORT_LIMIT = 15
# Number of minutes the AC can be turned on
TIME_LIMIT = 15
# Now as a timedelta
TIME_LIMIT_D = datetime.timedelta(minutes=TIME_LIMIT)


class Temperature(Thread):

    def __init__(self, car_control, target_temp, main, status, time=None):
        super(Temperature, self).__init__()
        self.main = main
        self.car_control = car_control
        self.target_temp = float(target_temp)
        self.response = None
        self.time = time
        self.status = status
        self.start()
        self.deactivated = False
        self.deactivate_lock = Lock()

    def run(self):
        if self.time is None:
            self.activate()

        else:
            # Parse time data
            activate_datetime = datetime.datetime.strptime(self.time, "%H:%M")
            now_datetime = datetime.datetime.now()
            # Set the activate datetime to be the next day if the time is set in the past
            if activate_datetime.timestamp() < now_datetime.timestamp():
                activate_datetime += datetime.timedelta(days=1)
            # Find out how long we should wait before activating
            difference = activate_datetime - (now_datetime + TIME_LIMIT_D)
            # Activate immediately if we have less time available than required to warm up car
            if difference.total_seconds() < TIME_LIMIT_D.total_seconds():
                pass
            else:
                # Wait
                sleep(difference.total_seconds())
            self.activate()

    def activate(self):
        # Tells CarControl to activate the AC to the given target_temp.
        # Format to be sent:
        # { "enable": true, "temperature": target_temp }
        with self.deactivate_lock:
            if not self.deactivated:
                di = {"enabled": True, "temperature": self.target_temp}
                data = json.dumps(di)
                self.response = self.car_control.set_AC(data)
                self.status.add_listener(self.battery_level_changed, "battery_level")
            else:
                return
        sleep(TIME_LIMIT)
        self.deactivate()

    def deactivate(self, err=None):
        # Tells CarControl to deactivate AC
        # Can be called from batteryListener or main
        # An error message (code 6 or 7) should be sent from BatteryListener to Main if BatteryListener calls
        # deactivate.
        # An ok-message should be sent from main to web server if main is the source (then it is likely that the user
        # has canceled the AC). This can be sent via the CarControl-class.

        with self.deactivate_lock:
            if not self.deactivated:
                self.deactivated = True
                di = {"enabled": False, "temperature": None}
                data = json.dumps(di)
                self.response = self.car_control.set_AC(data)
                # deregister
                self.status.remove_listener(self.battery_level_changed, "battery_level")
                # don't remember us
                self.main.AC_controller = None
                # send any error messages
                if err is not None:
                    self.main.add_error_message(err, "")

    def update_temperature(self, target_temp):
        self.target_temp = target_temp
        self.activate()

    def battery_level_changed(self, battery_level):
        if battery_level < AC_ABORT_LIMIT:
            self.deactivate(7)


