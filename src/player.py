from abc import abstractmethod
from media import MediaInfo, MediaControl


class Player(MediaControl, MediaInfo):

    CHUNK = 1024
    stream = None
    event = None

    @abstractmethod
    def playback_position(self):
        pass
