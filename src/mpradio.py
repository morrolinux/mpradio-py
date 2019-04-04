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
from media import MediaControl, MediaInfo


class Mpradio:

    bt_daemon = None
    control_pipe = None
    remote_event = None
    remote_msg = None
    media_control_methods = None
    media_info_methods = None
    check_remotes_termination = None

    player = None
    encoder = None
    output = None

    def __init__(self):
        signal.signal(signal.SIGUSR1, self.handler)
        signal.signal(signal.SIGINT, self.termination_handler)
        self.remote_msg = dict()
        self.check_remotes_termination = threading.Event()
        self.remote_event = threading.Event()       # Event for signaling control thread(s) events to main thread
        self.control_pipe = ControlPipe(self.remote_event)
        # Bluetooth setup (only if a2dp is supported)
        if which("bluealsa") is not None:
            self.bt_daemon = BluetoothDaemon()
        self.media_control_methods = [f for f in dir(MediaControl)
                                      if not f.startswith('_') and callable(getattr(MediaControl, f))]
        self.media_info_methods = [f for f in dir(MediaInfo)
                                   if not f.startswith('_') and callable(getattr(MediaInfo, f))]
        self.player = StoragePlayer()
        self.encoder = Encoder()
        # probe which platform are we running on for automatic output detection
        if platform.machine() == "x86_64":
            self.output = AnalogOutput()
        else:
            self.output = FmOutput()

    def handler(self, signum, frame):
        print("received signal", signum)

    def termination_handler(self, signum, frame):
        print("stopping threads and clean termination...")
        self.check_remotes_termination.set()
        self.control_pipe.stop()
        self.player.stop()
        self.encoder.stop()
        self.output.stop()
        quit(0)

    def run(self):
        # TODO: use some synchronization mechanism to ensure consistency player -> encoder -> output
        threading.Thread(target=self.player.run).start()
        self.encoder.run()
        self.output.start()

        threading.Thread(target=self.control_pipe.listen, args=(self.remote_msg,)).start()
        # TODO: start other control threads here (remotes) using the same event for all

        threading.Thread(target=self.check_remotes).start()

        # pre-buffer
        data = self.player.stream.stdout.read(self.player.CHUNK)

        # play stream
        while True:
            try:
                if data is not None:
                    self.encoder.stream.stdin.write(data)
                else:                                               # avoid 100% CPU when player is paused
                    raise AttributeError
                encoded = self.encoder.stream.stdout.read(self.player.CHUNK)    # must be non-blocking
                if encoded is not None:                             # send the encoded data to output, if any
                    self.output.stream.stdin.write(encoded)
                else:
                    raise AttributeError
            except AttributeError:
                time.sleep(0.02)
                # print("attr. error - data is None")
            # advance the "play head"
            data = self.player.stream.stdout.read(self.player.CHUNK)    # must be non-blocking
            # print("advance the play head")

    def check_remotes(self):
        while not self.check_remotes_termination.is_set():
            time.sleep(0.2)
            if self.remote_event.is_set():
                self.remote_event.clear()
                if self.remote_msg["command"][0] in self.media_control_methods:
                    exec("self.player."+self.remote_msg["command"][0]+"()")
                    # exec("threading.Thread(target="+"self.player." + self.remote_msg["command"][0] + ").start()")
                elif self.remote_msg["command"][0] in self.media_info_methods:
                    print(eval("self.player."+self.remote_msg["command"][0]+"()"))
                    # TODO: check the source (remote_msg["source"] and send the reply accordingly
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
    mpradio.run()




