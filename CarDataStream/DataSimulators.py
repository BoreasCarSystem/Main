from DataSimulation import *
from time import sleep,time
import json

class Battery(ThreadedDataGenerator):

    CHARGE_RATE_IDLE = -0.00001
    CHARGE_RATE_DRIVING = 0.0001
    CHARGE_RATE_IDLE_BUT_POWER_USE = -0.01

    def __init__(self, name, level=100, charge_rate=CHARGE_RATE_IDLE_BUT_POWER_USE):
        super(Battery, self).__init__(name)
        self.level = level
        self.max_level = 100
        self.charge_rate = charge_rate

    def generate(self):
        while True:
            value = round(self.level + self.charge_rate, 5)
            if value <= 100 and value >= 0:
                self.level = value
            else:
                if value < 1:
                    self.alue = 0
                else:
                    self.level = 100.0
            item = {"name":"battery_level", "value":self.level, "timestamp":time()}
            self.send(self.name, item)
            sleep(0.1)
            if self.should_stop:
                return





class JsonDataGenerator(ThreadedDataGenerator):

    def __init__(self, name, filename):
        super(JsonDataGenerator, self).__init__(name)
        self.filename = filename
        self.data_list = self.read_json_from_file(filename)
        self.sent_items_last_timestamp = dict()

    def generate(self):
        now = time()
        diff = now - self.data_list[0]["timestamp"]

        adjusted_time = time() - diff

        for item in self.data_list:

            while item["timestamp"] > adjusted_time:
                adjusted_time = time() - diff
            item["timestamp"] = time()
            self.send(self.name, item)
            if self.should_stop:
                return
        print("All data consumed!")
        return

    def read_json_from_file(filename):
        with open(filename) as data:

            json_list = list()
            for line in data:
                json_line = json.loads(line)
                json_list.append(json_line)

            return json_list

generator = Battery("Battery", charge_rate=-1)
generator.subscribe(observer=PrintValueAndSourceObserver())
generator.start()