import os
import time


class ControlPipe:
    path = "/tmp/mpradio_bt"
    control = None
    termination = None
    event = None

    def __init__(self, termination, event):
        self.fifo_setup()
        self.termination = termination
        self.event = event

    def fifo_setup(self):
        try:
            os.mkfifo(self.path)
        except FileExistsError:
            print("fifo already exists")
        self.control = os.open(self.path, os.O_RDONLY | os.O_NONBLOCK)

    def listen(self, msg):
        while not self.termination.is_set():
            time.sleep(0.5)
            cmd = os.read(self.control, 100).decode().strip().lower().split()

            if len(cmd) > 0:
                msg["command"] = cmd
                msg["source"] = "control_pipe"
                self.event.set()
