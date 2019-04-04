from abc import ABC, abstractmethod


class MediaControl(ABC):

    Ciao = "ciao"

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def resume(self):
        pass

    @abstractmethod
    def pause(self):
        pass

    @abstractmethod
    def next(self):
        pass

    @abstractmethod
    def previous(self):
        pass

    @abstractmethod
    def repeat(self):
        pass

    @abstractmethod
    def fast_forward(self):
        pass

    @abstractmethod
    def rewind(self):
        pass

    @abstractmethod
    def stop(self):
        pass


class MediaInfo(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def song_name(self):
        pass

    @abstractmethod
    def song_artist(self):
        pass

    @abstractmethod
    def song_year(self):
        pass

    @abstractmethod
    def song_album(self):
        pass
