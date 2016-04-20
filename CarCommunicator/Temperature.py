import json
from threading import Thread, Lock, Timer
from time import sleep
from time import strftime, strptime, time, mktime

AC_NOT_START_LIMIT = 25
AC_ABORT_LIMIT = 15
# Number of minutes the AC can be turned on
TIME_LIMIT = 1


class Temperature(Thread):

    def __init__(self, car_control, target_temp, main, status, time=None):
        super(Temperature, self).__init__(daemon=True)
        self.main = main
        self.car_control = car_control
        self.target_temp = float(target_temp)
        self.response = None
        self.time = time
        self.status = status
        self.deactivated = False
        self.deactivate_lock = Lock()
        self.timer = None
        self.start()

    def run(self):


        if self.time is None:
            self.activate()

        else:
            # Parse time data
            print(self.time)
            self.time = self.time + strftime("%Y-%m-%d")
            activate_time = strptime(self.time, "%H:%M%Y-%m-%d")

            print(activate_time)

            timedelta = mktime(activate_time) - time()


            if 0 <= timedelta < TIME_LIMIT*60:
                print("Temperature: Activated AC")
                self.activate()
            else:
                if timedelta < 0:
                    timedelta += 24 * 60 * 60
                print("Temperature: Set timer for ", timedelta, " seconds")
                Timer(timedelta, self.activate).start()

    def activate(self):
        print("AC: Activates")

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
        print("AC: før timer")
        self.timer = Timer(TIME_LIMIT*60, self.deactivate)
        self.timer.start()
        print("AC: etter timer")

    def deactivate(self, err=None):
        # Tells CarControl to deactivate AC
        # Can be called from batteryListener or main
        # An error message (code 6 or 7) should be sent from BatteryListener to Main if BatteryListener calls
        # deactivate.
        # An ok-message should be sent from main to web server if main is the source (then it is likely that the user
        # has canceled the AC). This can be sent via the CarControl-class.
        if self.timer is not None:
            self.timer.cancel()

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


