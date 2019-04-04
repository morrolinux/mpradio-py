from abc import ABC, abstractmethod


class Output(ABC):

    stream = None

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass
