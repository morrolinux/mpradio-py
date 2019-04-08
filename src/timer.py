import time
import threading


class Timer:

    __time = None
    __paused = False
    __termination = None

    def __init__(self, start_time=0):
        self.__termination = threading.Event()
        self.__time = start_time

    def count(self):
        while not self.__termination.is_set():
            time.sleep(1)
            if not self.__paused:
                self.__time += 1

    def start(self):
        self.__paused = False
        threading.Thread(target=self.count).start()

    def stop(self):
        self.__termination.set()

    def pause(self):
        self.__paused = True

    def resume(self):
        self.__paused = False

    def reset(self):
        self.__time = 0

    def get_time(self):
        return self.__time
