from CarDataStream.DataSimulators import *



class DataStream(DataGenerator):


    def __init__(self, generators):


    def add_generator(self, generator):
        if isinstance(generator, DataGenerator):
            self.generators.append(generator)

