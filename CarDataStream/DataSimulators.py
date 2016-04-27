from DataGenerators import *
from time import sleep,time
import json
from threading import Timer



class WasherFluid(ThreadedDataGenerator):

    def __init__(self, name, level=100.0, interval=20.0):
        super(WasherFluid, self).__init__(name)
        self.level = level
        self.interval=interval
        self.max_level = 100.0

    def generate(self):
        while True:

            value = self.level - 2.0
            if value <= 100 and value >= 0:
                self.level = value
            else:
                if value < 0:
                    self.level = 0.0
                else:
                    self.level = 100.0

            item = {"name":"washerfluid_level", "value":self.level, "timestamp":time()}
            self.send(self.name,item)
            sleep(self.interval)


class Temperature(ThreadedDataGenerator):

    def __init__(self, name, outside=15.0, current=15.0, target=0, ac_on=False):
        super(Temperature, self).__init__(name)
        self.outside = outside
        self.current = current
        self.target = target
        self.ac_on = ac_on

    def generate(self):

        while True:
            if self.ac_on:
                if abs(self.target - self.current) < 0.2:
                    self.current = self.target
                elif self.target > self.current:
                    self.current += 0.2
                elif self.target < self.current:
                    self.current -= 0.2
            else:
                if abs(self.outside - self.current) < 0.1:
                    self.current = self.outside
                elif self.outside > self.current:
                    self.current += 0.1
                elif self.outside < self.current:
                    self.current -= 0.1
            self.current = round(self.current, 1)
            item = {"name":"temperature", "value":self.current, "timestamp":time()}
            self.send(self.name, item)
            sleep(1)





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
                    self.level = 0
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


        with open(self.filename) as data:
            for line in data:
                item = json.loads(line)
                while item["timestamp"] > adjusted_time:
                    adjusted_time = time() - diff
                item["timestamp"] = time()
                self.send(self.name, item)
                if self.should_stop:
                    return
            self.generate()


    def read_json_from_file(self, filename):
        with open(filename) as data:

            json_list = list()
            for line in data:
                json_line = json.loads(line)
                json_list.append(json_line)

            return json_list
