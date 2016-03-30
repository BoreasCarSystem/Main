from DataGenerators import *
from DataSimulators import *
from requests import request, post, get
from collections import defaultdict
from threading import Timer, Thread
from time import sleep
import pprint


class RepeatingTimer(Thread):

    pass


class DataStream():



    def __init__(self, merged_generator):
        self.generator = None
        if isinstance(merged_generator, MergeManyGenerator):
            self.generator = merged_generator
            self.generator.subscribe(on_next=self.recieve)
            self.data_dict = dict()



    def start(self):
        if self.generator:
            self.generator.start()
        self.send()



    def recieve(self, source, value):
        key = value["name"]
        value = value["value"]
        self.data_dict[key] = value



    def send(self):


        r = post(url="http://localhost:34444", json=(self.data_dict))

        #pretty_print_dict(self.data_dict)


        Timer(1.0, self.send).start()



def pretty_print_dict(dict):
    pp = pprint.PrettyPrinter()
    pp.pprint(dict)



generator = MergeManyGenerator(generators=[JsonDataGenerator("Json", "downtown-west.json")])
stream = DataStream(generator)
stream.start()
