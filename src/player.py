from abc import abstractmethod
from media import MediaInfo, MediaControl
import threading
import subprocess
import time


class Player(MediaControl, MediaInfo):

    CHUNK = 1024 * 8    # set to 8192 for it to perform well on the orignal Pi 1. For any newer model, 2048 will do.
    SLEEP_TIME = 0.035
    output_stream = None
    ready = None

    def __init__(self):
        self.ready = threading.Event()

    @abstractmethod
    def playback_position(self):
        pass

    """
    legacy method for generating silence
    def silence(self, silence_time=1.2):
        tmp_stream = self.output_stream
        self.output_stream = subprocess.Popen(["sox", "-n", "-r", "48000", "-b", "16", "-c", "1", "-t", "wav", "-",
                                               "trim", "0", str(silence_time)],
                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        time.sleep(silence_time)
        self.output_stream = tmp_stream
    """
