from abc import abstractmethod
from media import MediaInfo, MediaControl


class Player(MediaControl, MediaInfo):

    CHUNK = 8192
    SLEEP_TIME = 0.03
    stream = None
    event = None    # TODO: maybe delete?

    @abstractmethod
    def playback_position(self):
        pass
