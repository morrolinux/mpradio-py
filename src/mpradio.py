#!/usr/bin/env python3
import signal
import os
import threading
import time
from encoder import Encoder
from configuration import config    # must be imported before all other modules (dependency)
from bluetooth_remote import BtRemote
from bluetooth_player import BtPlayer
from bluetooth_player_lite import BtPlayerLite
from fm_output import FmOutput
from analog_output import AnalogOutput
from storage_player import StoragePlayer
from control_pipe import ControlPipe
from media import MediaControl, MediaInfo
import platform
from subprocess import call
import json


class Mpradio:

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
        super().__init__()
        signal.signal(signal.SIGUSR1, self.handler)
        signal.signal(signal.SIGINT, self.termination_handler)
        self.remote_msg = dict()
        self.remotes_termination = threading.Event()
        self.remote_event = threading.Event()       # Event for signaling control thread(s) events to main thread
        self.reply_event = threading.Event()
        self.control_pipe = ControlPipe(self.remote_event, self.remote_msg)
        self.bt_remote = BtRemote(self.remote_event, self.remote_msg)

        # TODO: maybe refractor into player_methods and always eval()?
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
        self.encoder.run()
        self.output.run()
        self.player.set_out_stream(self.output.input_stream)
        self.player.run()
        self.bt_remote.run()
        self.control_pipe.listen()
        if platform.machine() != "x86_64":
            from gpio_remote import GpioRemote
            self.gpio_remote = GpioRemote(self.remote_event, self.remote_msg)
            self.gpio_remote.run()

        threading.Thread(target=self.check_remotes).start()

        '''
        # play stream
        while True:
            self.player.ready.wait()
            data = self.player.output_stream.read()

            if data is not None:
                self.output.ready.wait()
                self.output.input_stream.write(data)
                t = 0.005
                wait_time = ((len(data)/4)/44.1) * 0.001
                # print("just read", len(data), "bytes. sleeping for", wait_time, "-", t)
                if wait_time >= t:
                    wait_time -= t
                time.sleep(wait_time)
            # print("advancing playhead...")
        '''

    def check_remotes(self):
        while not self.remotes_termination.is_set():
            time.sleep(0.02)
            if self.remote_event.is_set():
                self.remote_event.clear()
                try:
                    cmd = self.remote_msg["command"]
                except KeyError:
                    continue

                if cmd[0] in self.media_control_methods:
                    exec("self.player."+cmd[0]+"()")
                elif cmd[0] in self.media_info_methods:
                    result = eval("self.player."+cmd[0]+"()")
                    if self.remote_msg["source"] == "bluetooth":
                        self.bt_remote.reply(result)
                elif cmd[0] == "bluetooth":
                    if cmd[1] == "attach":
                        if self.player.__class__.__name__ == "BtPlayerLite":
                            continue
                        tmp = BtPlayerLite(cmd[2])
                        self.player.stop()
                        self.player = tmp
                        self.player.set_out_stream(self.output.input_stream)
                        self.player.run()
                        print("bluetooth attached")
                    elif cmd[1] == "detach":
                        if self.player.__class__.__name__ != "BtPlayerLite":
                            continue
                        self.player.stop()
                        self.player = StoragePlayer()
                        self.player.set_out_stream(self.output.input_stream)
                        self.player.run()
                        # self.player.ready.wait()
                        print("bluetooth detached")
                elif cmd[0] == "system":
                    if cmd[1] == "poweroff":
                        self.player.pause()
                        call(["sudo", "poweroff"])
                    elif cmd[1] == "reboot":
                        self.player.pause()
                        call(["sudo", "reboot"])
                    else:
                        call(["sudo"] + cmd[1:])
                elif cmd[0] == "play":
                    if self.player.__class__.__name__ != "StoragePlayer":
                        continue
                    what = json.loads(self.remote_msg["data"])
                    self.player.play_on_demand(what)
                elif cmd[0] == "playlist":
                    try:
                        with open(config.get_playlist_file()) as file:        # TODO: implement in player
                            pl = str(json.load(file))
                            self.bt_remote.reply(pl)
                    except FileNotFoundError:
                        pass
                elif cmd[0] == "library":
                    try:
                        with open(config.get_library_file()) as file:
                            lib = str(json.load(file))
                            self.bt_remote.reply(lib)
                    except FileNotFoundError:
                        pass
                elif cmd[0] == "config":
                    if cmd[1] == "get":
                        self.bt_remote.reply(config.to_json())
                    elif cmd[1] == "set":
                        cfg = self.remote_msg["data"]
                        self.apply_configuration(cfg)
                    elif cmd[1] == "reload":        # TODO: remove. this is for testing purposes only
                        self.reload_configuration()
                else:
                    print("unknown command received:", cmd)
                self.remote_msg.clear()    # clean for next usage

        # Remote checker termination
        self.control_pipe.stop()
        self.bt_remote.stop()
        if self.gpio_remote is not None:
            self.gpio_remote.stop()

    def apply_configuration(self, cfg):
        config.load_json(cfg)
        self.reload_configuration()

    def reload_configuration(self):
        self.player.pause()         # player must be paused/silenced to avoid audio feed loop on fm transmission
        self.encoder.reload()       # encoded must be reloaded to avoid broken pipe
        self.output.check_reload()  # don't restart output if not needed
        self.player.resume()


if __name__ == "__main__":
    print('mpradio main PID is:', os.getpid())

    mpradio = Mpradio()
    mpradio.run()




