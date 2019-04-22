from abc import ABC, abstractmethod


class Output(ABC):

    stream = None

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def stop(self):
        pass
