from abc import abstractmethod
from media import MediaInfo, MediaControl
import time
from mp_io import MpradioIO


class Player(MediaControl, MediaInfo):

    CHUNK = 2048
    SLEEP_TIME = 0.035

    out = None
    event = None    # TODO: maybe delete?
    _tmp_stream = None
    silence_sound = None
    __wav_header = (b'RIFF\xff\xff\xff\xffWAVEfmt \x10\x00\x00\x00\x01\x00\x02\x00D\xac\x00\x00\x10\xb1'
                    b'\x02\x00\x04\x00\x10\x00LIST\x1a\x00\x00\x00INFOISFT\x0e\x00\x00\x00Lavf58.20.100'
                    b'\x00data\xff\xff\xff\xff\x00')
    __wav_silence = b'\x00'
    __wav_end = b'xee=\x11'

    def __init__(self):
        # Craft silence sound
        self.silence_sound = MpradioIO()
        self.silence_sound.write(self.__wav_header)
        for _ in range(0, 1000):
            self.silence_sound.write(self.__wav_silence)
        self.silence_sound.write(self.__wav_end)

    @abstractmethod
    def playback_position(self):
        pass

    def silence(self, silence_time=0.8):
        self._tmp_stream = self.out
        self.out = self.silence_sound
        time.sleep(silence_time)
