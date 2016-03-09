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

    def generate(self):
        pass

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


# Threaded version of the DataGenerator. Will run the generate() method on a seperate thread, not blocking the main program.
class ThreadedDataGenerator(DataGenerator):

    def __init__(self, name):
        super(ThreadedDataGenerator, self).__init__(name)
        self.thread = None

    def start(self):
        self.should_stop = False
        self.is_started = True
        self.thread = Thread(target=self.generate)
        self.thread.start()
        return self

    def merge(self, other_generator):
        return MergedGenerator(self, other_generator)

# Generator that consists of two other generators. Sub-generators should be of type ThreadedDataGenerator.
class MergedGenerator(DataGenerator):

    def __init__(self, generator1, generator2):
        super(MergedGenerator, self).__init__("Merged")
        print("Merging generators...")
        if isinstance(generator1, ThreadedDataGenerator) and isinstance(generator2, ThreadedDataGenerator):
            self.generator1 = generator1
            self.generator2 = generator2
            self.generator1.subscribe(on_next=self.merge_generate)
            self.generator2.subscribe(on_next=self.merge_generate)
        else:
            raise Exception("Cant merge non-threaded generators!")

    def start(self):
        self.should_stop = False
        self.is_started = True
        self.generator1.start()
        self.generator2.start()


    def stop(self):
        self.generator1.should_stop = True
        self.generator2.should_stop = True

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


