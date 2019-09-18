from typing import Union
import time


class BytearrayIO:

    def __init__(self):
        self.buf_size = None
        self.buf = None
        self.mv = None
        self.__last_r = 0
        self.__last_w = 0
        self.__wrap_around_at = None
        self.__write_completed = False
        self.__terminating = False
        self.__chunk_size = 1024 * 20
        self.out_stream = None

    def set_out_stream(self, out_s, buf_size=0):
        self.out_stream = out_s
        if buf_size > 0:
            self.buf_size = 1024 * 1000 * buf_size
            self.buf = bytearray(self.buf_size)
            self.mv = memoryview(self.buf)
            self.__wrap_around_at = self.buf_size
            self.start_output()

    def silence(self, silent=True):
        pass

    def read(self, size):
        if self.__terminating:
            return

        # reader wrap around when reaching last written byte
        if self.__last_r == self.__wrap_around_at:
            self.__last_r = 0
            print("read wrap around at", self.__wrap_around_at)

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
        # print("reading size:", rs)
        if rs == 0:
            time.sleep(0.001)

        end = start + rs
        self.__last_r = end
        return self.buf[start:end]

    def write(self, b: Union[bytes, bytearray]):
        if self.buf_size is not None:
            size = len(b)

            # write wrap around
            if self.__last_w + size > self.buf_size:
                self.__wrap_around_at = self.__last_w
                self.__last_w = 0
                # print("write wrap around at", self.__wrap_around_at)

            start = self.__last_w
            self.__last_w = start + size
            try:
                self.mv[start:self.__last_w] = b
            except ValueError:
                print("Value error. len(buf) = ", len(self.buf), "last_w = ", self.__last_w)
        else:
            try:
                self.out_stream.write(b)
            except BrokenPipeError:
                print("Broken pipe to output")

    def start_output(self):
        import threading
        threading.Thread(target=self.__write_to_pipe).start()

    def __write_to_pipe(self):
        while not self.__terminating:
            try:
                self.out_stream.write(self.read(self.__chunk_size))
            except AttributeError:
                time.sleep(0.01)

    def set_write_completed(self):
        self.__write_completed = True

    def is_read_completed(self):
        if self.__last_w > 0 and self.__last_w == self.__last_r and self.__write_completed:
            return True
        else:
            return False

    def seek_to_start(self):
        del self.buf
        del self.mv
        self.buf = bytearray(self.buf_size)
        self.mv = memoryview(self.buf)
        self.__last_r = 0
        self.__last_w = 0

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
