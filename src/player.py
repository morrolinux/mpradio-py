from abc import abstractmethod
from media import MediaInfo, MediaControl
import subprocess
import time


class Player(MediaControl, MediaInfo):

    CHUNK = 2048
    SLEEP_TIME = 0.035
    out = None
    _tmp_stream = None

    @abstractmethod
    def playback_position(self):
        pass

    def silence(self, silence_time=0.8):
        self._tmp_stream = self.out
        self.out = subprocess.Popen(["sox", "-n", "-r", "48000", "-b", "16", "-c", "1", "-t", "wav", "-",
                                               "trim", "0", str(silence_time)],
                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        time.sleep(silence_time)
