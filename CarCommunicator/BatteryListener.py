
AC_NOT_START_LIMIT = 25
AC_ABORT_LIMIT = 15


class BatteryListener:

    def __init__(self, temperature_obj, status_obj):
        self.temperature = temperature_obj
        self.status = status_obj
        self.battery_level = None
        self.check_start_up()

    def update(self):
        self.battery_level = self.status.get_battery_level()
        if self.battery_level < AC_ABORT_LIMIT:
            self.temperature.deactivate(7)

    def check_start_up(self):
        self.battery_level = self.status.get_battery_level()
        if self.battery_level < AC_NOT_START_LIMIT:
            self.temperature.deactivate(6)
