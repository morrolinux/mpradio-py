from typing import Union


class BytearrayIO:

    def __init__(self):
        self.buf_size = 1024 * 10000
        self.buf = bytearray(self.buf_size)
        self.mv = memoryview(self.buf)
        self.last_r = 0
        self.last_w = 0
        self.__write_completed = False

    def silence(self, silent=True):
        pass

    def read(self, size=1024):
        print("read", size)  # non è effettivamente quanto viene letto ma quanto viene chiesto
        start = self.last_r
        end = min(self.last_r + size, self.last_w)  # don't read more data than available
        self.last_r = end
        return self.buf[start:end]

    def write(self, b: Union[bytes, bytearray]):
        size = len(b)
        print("wrote", size)
        start = self.last_w
        self.last_w = self.last_w + size
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
