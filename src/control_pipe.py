import os
import time
import threading
from configuration import config


class ControlPipe:
    __ctl_path = None
    __control = None
    __event = None
    __termination = None

    def __init__(self, event, message):
        self.__termination = threading.Event()
        self.__event = event
        self.__msg = message
        self.__ctl_path = config.get_ctl_path()
        self.fifo_setup()

    # TODO: always try to delete, then make fifo (cleanup events before starting)
    def fifo_setup(self):
        try:
            os.mkfifo(self.__ctl_path)
        except FileExistsError:
            pass
        self.__control = os.open(self.__ctl_path, os.O_RDONLY | os.O_NONBLOCK)

    def listen(self):
        threading.Thread(target=self.__listen).start()

    def __listen(self):
        while not self.__termination.is_set():
            time.sleep(0.2)
            cmd = os.read(self.__control, 100).decode().strip().lower().split()

            if len(cmd) > 0:
                self.__msg["command"] = cmd
                self.__msg["source"] = "control_pipe"
                self.__event.set()

    def stop(self):
        self.__termination.set()
