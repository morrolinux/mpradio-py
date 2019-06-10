from typing import Union
import time


class BytearrayIO:

    def __init__(self):
        self.buf_size = 1024 * 1000  # 1M
        self.buf = bytearray(self.buf_size)
        self.mv = memoryview(self.buf)
        self.last_r = 0
        self.last_w = 0
        self.wrap_around = False
        self.wrap_around_at = self.buf_size
        self.__write_completed = False

    def silence(self, silent=True):
        pass

    def read(self, size=1024):
        while True:

            if self.last_r == self.wrap_around_at:
                self.last_r = 0
                print("read wrap around at", self.wrap_around_at)

            start = self.last_r
            available = self.last_w - self.last_r

            # write wrap around detection and handling
            if available < 0:
                available = self.wrap_around_at - self.last_r

            # read what's possible
            rs = min(size, available)

            if rs == 0:
                print("buffer underrun")
                time.sleep(0.008)
                continue

            end = start + rs
            self.last_r = end
            return self.buf[start:end]

    def write(self, b: Union[bytes, bytearray]):
        size = len(b)

        # write wrap around
        if self.last_w + size > self.buf_size:
            self.wrap_around_at = self.last_w
            self.last_w = 0
            self.wrap_around = True
            print("write wrap around at", self.wrap_around_at)

        start = self.last_w
        self.last_w = start + size
        try:
            self.mv[start:self.last_w] = b
        except ValueError:
            print("Value error. len(buf) = ", len(self.buf), "last_w = ", self.last_w)

    def set_write_completed(self):
        self.__write_completed = True

    def is_read_completed(self):
        if self.last_w > 0 and self.last_w == self.last_r and self.__write_completed:
            return True
        else:
            return False

    def seek_to_start(self):
        self.last_r = 0

    def stop(self):
        pass

    # IoBase dummy interface implementation for pyav
    def seek(self, offset: int, whence: int = ...):
        pass
