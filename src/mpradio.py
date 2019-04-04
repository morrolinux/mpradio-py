#!/usr/bin/env python3
import signal
import platform
import os
import threading
import time
from shutil import which
from encoder import Encoder
from bluetooth_daemon import BluetoothDaemon
from bluetooth_player import BtPlayer
from fm_output import FmOutput
from analog_output import AnalogOutput
from storage_player import StoragePlayer
from control_pipe import ControlPipe
from media import MediaControl


class Mpradio:

    bt_daemon = None
    control_pipe = None
    control_pipe_termination = None     # TODO: check if really needed or refractor
    remote_event = None
    remote_msg = None
    media_control_functions = None

    player = None
    encoder = None
    output = None

    def __init__(self):
        signal.signal(signal.SIGUSR1, self.handler)
        signal.signal(signal.SIGUSR2, self.handler)
        signal.signal(signal.SIGINT, self.termination_handler)
        self.remote_event = threading.Event()       # Event for signaling worker thread events to main thread
        self.control_pipe_termination = threading.Event()    # Event for signaling the worker thread to stop
        self.remote_msg = dict()
        self.control_pipe = ControlPipe(self.control_pipe_termination, self.remote_event)
        # Bluetooth setup (only if a2dp is supported)
        if which("bluealsa") is not None:
            self.bt_daemon = BluetoothDaemon()
        self.media_control_functions = [f for f in dir(MediaControl)
                                        if not f.startswith('_') and callable(getattr(MediaControl, f))]

        # TODO: read settings INSIDE the class? es: player.reload_config()
        self.player = StoragePlayer()
        # self.player.run()
        threading.Thread(target=self.player.run).start()
        self.encoder = Encoder()
        self.encoder.run()
        # probe which platform are we running on for automatic output detection
        if platform.machine() == "x86_64":
            self.output = AnalogOutput()
        else:
            self.output = FmOutput()
        self.output.start()

    def handler(self, signum, frame):
        print("received signal", signum)

    def termination_handler(self, signum, frame):
        print("stopping threads and clean termination...")
        self.control_pipe_termination.set()
        self.player.stop()
        self.encoder.stop()
        self.output.stop()
        quit(0)

    def run(self):
        threading.Thread(target=self.control_pipe.listen, args=(self.remote_msg,)).start()
        # TODO: start other control threads here (remotes) using the same event for all

        # pre-buffer
        data = self.player.stream.stdout.read(self.player.CHUNK)

        # play stream
        while True:
            try:
                if data is not None:
                    self.encoder.stream.stdin.write(data)
                else:                                               # avoid 100% CPU when player is paused
                    time.sleep(0.02)
                encoded = self.encoder.stream.stdout.read(self.player.CHUNK)    # must be non-blocking
                if encoded is not None:                             # send the encoded data to output, if any
                    self.output.stream.stdin.write(encoded)
                # advance the "play head"
                data = self.player.stream.stdout.read(self.player.CHUNK)    # must be non-blocking
                self.check_remotes()
            except AttributeError:
                data = None
                print("attr. error - data is None")
                time.sleep(0.02)

    def check_remotes(self):
        if self.remote_event.is_set():
            self.remote_event.clear()
            if self.remote_msg["command"][0] in self.media_control_functions:
                #exec("self.player."+self.remote_msg["command"][0]+"()")
                exec("threading.Thread(target="+"self.player." + self.remote_msg["command"][0] + ").start()")
            elif self.remote_msg["command"][0] == "bluetooth":
                if self.remote_msg["command"][1] == "attach":
                    self.player.stop()
                    self.player = BtPlayer(self.remote_msg["command"][2])
                    threading.Thread(target=self.player.run).start()
                    print("bluetooth attached")
                elif self.remote_msg["command"][1] == "detach":
                    self.player.stop()
                    self.player = StoragePlayer()
                    threading.Thread(target=self.player.run).start()
                    print("bluetooth detached")
            else:
                print("unknown command received")
            self.remote_msg.clear()    # clean for next usage


if __name__ == "__main__":
    print('mpradio main PID is:', os.getpid())

    mpradio = Mpradio()
    print("mpradio created")
    mpradio.run()




