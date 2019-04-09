import subprocess
import signal
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK, path
import time
from timer import Timer
from player import Player
from playlist import Playlist
from rds import RdsUpdater
import threading
import json
import platform


class StoragePlayer(Player):

    __tmp_out = None
    __terminating = False
    __playlist = None
    __now_playing = None
    __timer = None
    __resume_file = ""
    __rds_updater = None

    def __init__(self):
        super().__init__()
        self.__playlist = Playlist()
        if platform.machine() == "x86_64":
            self.__resume_file = "resume.json"
        else:
            self.__resume_file = "/home/pi/resume.json"
        self.__rds_updater = RdsUpdater()

    def playback_position(self):
        return self.__timer.get_time()

    def __update_playback_position(self):
        while not self.__terminating:
            if self.__now_playing is not None:
                self.__now_playing["position"] = self.__timer.get_time()
            with open(self.__resume_file, "w") as f:
                j = json.dumps(self.__now_playing)
                f.write(j)
            time.sleep(5)

    def __retrive_last_boot_playback(self):
        if not path.isfile(self.__resume_file):
            self.__timer = Timer()  # start the timer from 0
            return
        with open(self.__resume_file) as file:
            song = json.load(file)
        if song is not None:
            self.__playlist.add(song)

        try:
            self.__timer = Timer(song["position"])  # resume the timer from previous state
        except TypeError:
            self.__timer = Timer()

    def run(self):
        self.__retrive_last_boot_playback()
        self.__timer.start()
        self.__rds_updater.run()
        threading.Thread(target=self.__update_playback_position).start()
        for song in self.__playlist:
            if not self.__terminating:
                self.__now_playing = song
                print("playing:", song["path"])
                # print("playlist:", [song["path"] for song in self.__playlist.elements()])
                print("........................")
                self.play(song)
            else:
                return 

    def play(self, song):

        resume_time = song.get("position")

        if resume_time is not None:
            res = str(resume_time)
        else:
            res = "0"

        self.__rds_updater.set(song)

        self.__tmp_out = None
        self.stream = subprocess.Popen(["ffmpeg", "-i", song["path"], "-ss", res, "-vn", "-f", "wav", "pipe:1"],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # set the player to non-blocking output:
        flags = fcntl(self.stream.stdout, F_GETFL)  # get current stdout flags
        fcntl(self.stream.stdout, F_SETFL, flags | O_NONBLOCK)
        # Wait until process terminates
        while self.stream.poll() is None:
            time.sleep(0.02)
        self.__timer.reset()

    def pause(self):
        if platform.machine() == "x86_64":
            pause_sound = "../sounds/stop1.wav"
        else:
            pause_sound = "/home/pi/mpradio/sounds/stop1.wav"
        self.stream.send_signal(signal.SIGSTOP)
        self.__tmp_out = self.stream.stdout
        self.stream.stdout = subprocess.Popen(["ffmpeg", "-i", pause_sound, "-vn", "-f", "wav", "pipe:1"],
                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        self.__timer.pause()

    def resume(self):
        if self.__tmp_out is not None:
            self.stream.stdout = self.__tmp_out
        self.stream.send_signal(signal.SIGCONT)
        self.__timer.resume()

    def next(self):
        self.stream.kill()

    def previous(self):
        self.__playlist.back(n=1)
        self.next()

    def repeat(self):
        self.__playlist.back()

    def fast_forward(self):
        pass

    def rewind(self):
        self.__playlist.back()
        self.next()

    def stop(self):
        self.stream.kill()
        self.__terminating = True
        self.__timer.stop()
        self.__rds_updater.stop()

    def song_name(self):
        return self.__now_playing["title"]

    def song_artist(self):
        return self.__now_playing["artist"]

    def song_year(self):
        return self.__now_playing["year"]

    def song_album(self):
        return self.__now_playing["album"]
