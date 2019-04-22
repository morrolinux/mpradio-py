#!/usr/bin/env python3
import signal
import os
import threading
import time
from encoder import Encoder
from configuration import config    # must be imported before all other modules (dependency)
from bluetooth_remote import BtRemote
from bluetooth_player import BtPlayer
from fm_output import FmOutput
from analog_output import AnalogOutput
from storage_player import StoragePlayer
from control_pipe import ControlPipe
from media import MediaControl, MediaInfo
import platform
from subprocess import call
import json


class Mpradio:

    bt_daemon = None
    control_pipe = None
    bt_remote = None
    gpio_remote = None
    remote_event = None
    remote_msg = None
    media_control_methods = None
    media_info_methods = None
    remotes_termination = None

    player = None
    encoder = None
    output = None

    def __init__(self):
        signal.signal(signal.SIGUSR1, self.handler)
        signal.signal(signal.SIGINT, self.termination_handler)
        self.remote_msg = dict()
        self.remotes_termination = threading.Event()
        self.remote_event = threading.Event()       # Event for signaling control thread(s) events to main thread
        self.reply_event = threading.Event()
        self.control_pipe = ControlPipe(self.remote_event, self.remote_msg)
        self.bt_remote = BtRemote(self.remote_event, self.remote_msg)
        # Bluetooth setup (only if a2dp is supported)
        # if which("bluealsa") is not None:
        #     self.bt_daemon = BluetoothDaemon()

        # TODO: maybe refractor into player_methods end always eval()?
        self.media_control_methods = [f for f in dir(MediaControl)
                                      if not f.startswith('_') and callable(getattr(MediaControl, f))]
        self.media_info_methods = [f for f in dir(MediaInfo)
                                   if not f.startswith('_') and callable(getattr(MediaInfo, f))]
        self.player = StoragePlayer()
        self.encoder = Encoder()

        if config.get_settings()["PIRATERADIO"]["output"] == "fm":
            self.output = FmOutput()
        else:
            self.output = AnalogOutput()

    def handler(self, signum, frame):
        print("received signal", signum)

    def termination_handler(self, signum, frame):
        print("stopping threads and clean termination...")
        self.remotes_termination.set()
        self.player.stop()
        self.encoder.stop()
        self.output.stop()
        quit(0)

    def run(self):
        # TODO: use some synchronization mechanism to ensure consistency player -> encoder -> output
        self.player.run()
        self.encoder.run()
        self.output.start()

        # TODO: start other control threads here (remotes) using the same event for all
        self.bt_remote.run()
        self.control_pipe.listen()
        if platform.machine() != "x86_64":
            from gpio_remote import GpioRemote
            self.gpio_remote = GpioRemote(self.remote_event, self.remote_msg)
            self.gpio_remote.run()

        threading.Thread(target=self.check_remotes).start()

        # wait for the player to spawn
        while self.player.stream is None:
            time.sleep(0.2)

        # pre-buffer
        data = self.player.stream.stdout.read(self.player.CHUNK)

        # play stream
        while True:
            try:
                if data is not None:
                    self.encoder.stream.stdin.write(data)
                else:                                               # avoid 100% CPU when player is paused
                    # print("waiting for player data")
                    raise AttributeError
                encoded = self.encoder.stream.stdout.read(self.player.CHUNK)    # must be non-blocking
                if encoded is not None:                             # send the encoded data to output, if any
                    self.output.stream.stdin.write(encoded)
                else:
                    # print("waiting for encoder data")
                    raise AttributeError
            except AttributeError:
                time.sleep(self.player.SLEEP_TIME)
            # advance the "play head"
            if self.player.stream is not None:
                data = self.player.stream.stdout.read(self.player.CHUNK)    # must be non-blocking

    def check_remotes(self):
        while not self.remotes_termination.is_set():
            time.sleep(0.2)
            if self.remote_event.is_set():
                self.remote_event.clear()
                try:
                    cmd = self.remote_msg["command"][0]
                except KeyError:
                    continue

                if cmd in self.media_control_methods:
                    exec("self.player."+cmd+"()")
                elif cmd in self.media_info_methods:
                    result = eval("self.player."+cmd+"()")
                    if self.remote_msg["source"] == "bluetooth":
                        self.bt_remote.reply(result)
                elif cmd == "bluetooth":
                    if self.remote_msg["command"][1] == "attach":
                        if self.player.__class__.__name__ == "BtPlayer":
                            continue
                        self.player.stop()
                        self.player = BtPlayer(self.remote_msg["command"][2])
                        self.player.run()
                        print("bluetooth attached")
                    elif self.remote_msg["command"][1] == "detach":
                        if self.player.__class__.__name__ != "BtPlayer":
                            continue
                        self.player.stop()
                        self.player = StoragePlayer()
                        self.player.run()
                        print("bluetooth detached")
                elif cmd == "system":
                    if self.remote_msg["command"][1] == "poweroff":
                        call(["sudo", "poweroff"])
                    elif self.remote_msg["command"][1] == "reboot":
                        call(["sudo", "reboot"])
                elif cmd == "play":         # TODO: check weather it is a problem or not to call this method from here
                    what = json.loads(self.remote_msg["data"])
                    threading.Thread(target=self.player.play, args=(what,)).start()     # TODO: remove thread here
                elif cmd == "playlist":
                    with open("/pirateradio/playlist.json") as file:        # TODO: implement in player
                        lib = str(json.load(file))
                        print("library:", lib)
                    self.bt_remote.reply(lib)
                else:
                    print("unknown command received:", cmd)
                self.remote_msg.clear()    # clean for next usage

        # Remote checker termination
        self.control_pipe.stop()
        self.bt_remote.stop()
        if self.gpio_remote is not None:
            self.gpio_remote.stop()


if __name__ == "__main__":
    print('mpradio main PID is:', os.getpid())

    mpradio = Mpradio()
    mpradio.run()




