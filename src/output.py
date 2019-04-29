from abc import ABC, abstractmethod
import threading


class Output(ABC):

    stream = None
    input_stream = None
    output_stream = None
    ready = None

    def __init__(self):
        self.ready = threading.Event()

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def stop(self):
        pass
