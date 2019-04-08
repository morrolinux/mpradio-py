import os
import time
import threading


class ControlPipe:
    ctl_path = "/tmp/mpradio_bt"
    control = None
    event = None
    termination = None

    def __init__(self, event):
        self.fifo_setup()
        self.termination = threading.Event()
        self.event = event

    def fifo_setup(self):
        try:
            os.mkfifo(self.ctl_path)
        except FileExistsError:
            pass
        self.control = os.open(self.ctl_path, os.O_RDONLY | os.O_NONBLOCK)

    def listen(self, msg):
        while not self.termination.is_set():
            time.sleep(0.2)
            cmd = os.read(self.control, 100).decode().strip().lower().split()

            if len(cmd) > 0:
                msg["command"] = cmd
                msg["source"] = "control_pipe"
                self.event.set()

    def stop(self):
        self.termination.set()
