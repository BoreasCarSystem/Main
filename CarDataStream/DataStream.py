from DataGenerators import *
from requests import request
from collections import defaultdict
from threading import Timer, Thread
from time import sleep


class RepeatingTimer(Thread):

    pass


class DataStream():

    def __init__(self, merged_generator):
        self.generator = None
        if isinstance(merged_generator, MergeManyGenerator):
            self.generator = merged_generator
            self.generator.subscribe(self.recieve)
            self.data_dict = dict(dict())



    def start(self):
        if self.generator:
            self.generator.start()
        self.send()



    def recieve(self, source, value):
        key = value["name"]
        self.data_dict[value["name"]] = value



    def send(self):





        Timer(1.0, self.send).start()





stream = DataStream(merged_generator=None).start()
