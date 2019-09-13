from typing import Union
import time


class BytearrayIO:

    def __init__(self):
        self.buf_size = 1024 * 1000  # 1M
        self.buf = bytearray(self.buf_size)
        self.mv = memoryview(self.buf)
        self.__last_r = 0
        self.__last_w = 0
        self.__wrap_around_at = self.buf_size
        self.__write_completed = False
        self.__available = 0
        self.__terminating = False
        self.out_stream = None

    def set_out_stream(self, out_s):
        self.out_stream = out_s

    def silence(self, silent=True):
        pass

    def read(self, size=16384):
        while True:
            if self.__terminating:
                break

            # buffer underrun protection by checking total amount of available data
            # note that this is an absolute value and doesn't consider wrap around(s)
            if self.__available <= 0:
                time.sleep(0.001)
                # print("buffer underrun. available =", self.__available)
                continue

            # reader wrap around when reaching last written byte
            if self.__last_r == self.__wrap_around_at:
                self.__last_r = 0
                print("read wrap around at", self.__wrap_around_at, "avail:", self.__available)

            start = self.__last_r

            # available data in the buffer (wrap around aware)
            # if margin > 0, the read head is following the write head: |--r--w--|
            # if margin < 0, the write head has wrapped around and is following/reaching the read head: |--w--r--|
            margin = self.__last_w - start

            # if the writer already wrapped around we still need to consume the buffer until the wrap around point
            if margin < 0:
                margin = self.__wrap_around_at - start
                # print("writer wrap around detected")

            # read what's available (could be lower than requested size)
            rs = min(size, margin)

            self.__available -= rs
            # print("now available:", self.available)

            end = start + rs
            self.__last_r = end
            return self.buf[start:end]

    def write(self, b: Union[bytes, bytearray]):
        if self.out_stream is None:
            size = len(b)

            # write wrap around
            if self.__last_w + size > self.buf_size:
                self.__wrap_around_at = self.__last_w
                self.__last_w = 0
                print("write wrap around at", self.__wrap_around_at)

            start = self.__last_w
            self.__last_w = start + size
            self.__available += size
            try:
                self.mv[start:self.__last_w] = b
            except ValueError:
                print("Value error. len(buf) = ", len(self.buf), "last_w = ", self.__last_w)
        else:
            self.out_stream.write(b)

    def set_write_completed(self):
        self.__write_completed = True

    def is_read_completed(self):
        if self.__last_w > 0 and self.__last_w == self.__last_r and self.__write_completed:
            return True
        else:
            return False

    def seek_to_start(self):
        self.__last_r = 0

    def stop(self):
        self.__terminating = True

    # IoBase dummy interface implementation for pyav
    def seek(self, offset: int, whence: int = ...):
        pass

    def tell(self):
        return 0

    def flush(self):
        pass

    def close(self):
        pass
