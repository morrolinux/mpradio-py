import io
import threading
from typing import Union


class MpradioIO(io.BytesIO):

    def __init__(self):
        super().__init__()
        self.__lock = threading.Lock()
        self.__last_r = 0
        self.__size = 0
        self.__write_completed = False

    def read(self, size=None):
        self.__lock.acquire()               # thread-safe lock
        self.seek(self.__last_r)            # Seek to last read position
        result = super().read(size)         # read the specified amount of bytes
        self.__last_r += len(result)        # update the last read position
        self.__size = self.seek(0, 2)       # seek to the end (prepare for next write)
        self.__lock.release()
        return result

    def write(self, b: Union[bytes, bytearray]):
        self.__lock.acquire()               # thread-safe lock
        super().write(b)                    # write
        self.__lock.release()               # release lock

    def set_write_completed(self):
        self.__write_completed = True

    def is_read_completed(self):
        if self.__size > 0 and self.__size == self.__last_r and self.__write_completed:
            return True
        else:
            return False

    def seek_to_start(self):
        self.__last_r = 0
