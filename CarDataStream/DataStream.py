from DataGenerators import *
from DataSimulators import *
from requests import request, post, get
from collections import defaultdict
from threading import Timer, Thread
from time import sleep
import pprint
import urllib

VERBOSE = False
DEBUG = False

temperature_simulator = None

class DataStream:

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


        try:
            r = post(url="http://localhost:34444", json=(self.data_dict))
            response = json.loads(r.content.decode("utf-8"))
            print(response, temperature_simulator.target, temperature_simulator.current)
            ac_enabled = response["AC_enabled"]
            ac_target = response["AC_target_temperature"]
            temperature_simulator.ac_on = ac_enabled
            temperature_simulator.target = ac_target
        except Exception as e:
            if DEBUG:
                print(e)
                print("Failed to send data to Main")
        if VERBOSE:
            pretty_print_dict(self.data_dict)
        Timer(1.0, self.send).start()


def pretty_print_dict(dict):
    pp = pprint.PrettyPrinter()
    pp.pprint(dict)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Datastream", )
    parser.add_argument("datafile_name", help="Optional. Provide a datafile in the OpenXC format of your own choice. Otherwise a default will be used.",
                        default="downtown-west.json", nargs="?")
    parser.add_argument("-v", "--verbose", help="Prints all generated data.", action="store_true")
    parser.add_argument("-d", "--debug", help="Prints debugmessages", action="store_true")
    args = parser.parse_args()
    VERBOSE = args.verbose
    DEBUG = args.debug

    temperature_simulator = Temperature("Temperature")
    battery_simulator = Battery("Battery")
    washerfluid_simulator = WasherFluid("WasherFluid")
    datafile_simulator = JsonDataGenerator("Json", args.datafile_name)

    generators = [
        datafile_simulator,
        battery_simulator,
        washerfluid_simulator,
        temperature_simulator,
    ]

    generator = MergeManyGenerator(generators=generators)
    stream = DataStream(generator)
    stream.start()