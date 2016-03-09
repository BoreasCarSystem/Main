from threading import Thread


# Baseclass. Dows not implement threading. Should never be instantiated.
class DataGenerator(object):

    def __init__(self, name):
        self.observers = list()
        self.on_nexts = list()
        self.should_stop = False
        self.is_started = False
        self.name = name

    def start(self):
        self.should_stop = False
        self.is_started = True
        self.generate()
        return self

    def stop(self):
        self.should_stop = True
        self.is_started = False

    def generate(self):
        return

    def subscribe(self, observer=None, on_next=None):

        if observer:
            if isinstance(observer, DataObserver):
                self.observers.append(observer)
            else:
                print(observer.__str__() + " is not of type DataObserver")
        if on_next and hasattr(on_next, '__call__'):
            self.on_nexts.append(on_next)
        return self

    def send(self, source, value):
        for observer in self.observers:
            observer.on_next(source, value)
        for on_next in self.on_nexts:
            on_next(source, value)

"""
Threaded version of the DataGenerator. Will run the generate() method on a seperate thread, not blocking the main program.
The generate method needs to call return if the should_stop variable is True.
"""
class ThreadedDataGenerator(DataGenerator):

    def __init__(self, name):
        super(ThreadedDataGenerator, self).__init__(name)
        self.thread = None

    def start(self):
        if (self.thread and not self.thread.is_alive()) or not self.thread:
            self.should_stop = False
            self.is_started = True
            self.thread = Thread(target=self.generate)
            self.thread.start()
        return self


class MergeManyGenerator(DataGenerator):

    def __init__(self, generators):
        super(MergeManyGenerator, self).__init__("Mergeparty")
        self.generators = list()
        for generator in generators:
            if isinstance(generator, ThreadedDataGenerator):
                self.generators.append(generator)
                generator.subscribe(on_next=self.merge_generate)
            else:
                raise Exception("Cant merge non-threaded generators!")

    def add_generator(self, generator):
        if isinstance(generator, DataGenerator):
            self.generators.append(generator)
            generator.subscribe(on_next=self.merge_generate)
            generator.start()

    def start(self):
        self.should_stop = False
        self.is_started = True
        for generator in self.generators:
            generator.start()

    def stop(self):
        self.should_stop = True
        self.is_started = False
        for generator in self.generators:
            generator.stop()

    def merge_generate(self, source, value):
        self.send(source, value)






class DataObserver(object):

    def on_next(self, source, value):
        pass

    def on_complete(self, generator):
        pass

class PrintValueAndSourceObserver(DataObserver):

    def on_next(self, source, value):
        print(source + ": " + str(value))



