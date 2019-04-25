from abc import ABC, abstractmethod


class Output(ABC):

    stream = None
    input_stream = None
    output_stream = None

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def stop(self):
        pass
