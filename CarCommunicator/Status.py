class Status:
    """ We need to create a connection between this class and the CarDataStream.
    This class SHOULD listen at port 34444, where CarDataStream MUST send its data.

    Every attribute has a get-method. We've made the get-methods for battery_level and temperature, since this is
    needed for sprint 1.
    """

    def __init__(self):
        self.all_listeners = set()
        self.battery_level = None
        self.temp = None

    def get_battery_level(self):
        """
        We're assuming battery levels are in percents.
        """
        return self.battery_level

    def get_temperature(self):
        return self.temp

    def notify_listeners(self):
        for listener in self.all_listeners:
            listener.update()

    def add_listener(self, listener):
        self.all_listeners.add(listener)

    def remove_listener(self, listener):
        self.all_listeners.remove(listener)
