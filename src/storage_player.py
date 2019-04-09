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
from configuration import Configuration


class StoragePlayer(Player):

    stream = None
    __tmp_stream = None
    __terminating = False
    __playlist = None
    __now_playing = None
    __timer = None
    __resume_file = None
    __rds_updater = None
    __config = None

    def __init__(self):
        super().__init__()
        self.__playlist = Playlist()
        self.__config = Configuration()
        self.__rds_updater = RdsUpdater()
        self.__resume_file = self.__config.get_resume_file()

    def playback_position(self):
        return self.__timer.get_time()

    def __update_playback_position_thread(self):
        while not self.__terminating:
            if self.__now_playing is not None:
                self.__now_playing["position"] = self.playback_position()
            with open(self.__resume_file, "w") as f:
                j = json.dumps(self.__now_playing)
                f.write(j)
            time.sleep(5)

    def __update_playback_position(self):
        threading.Thread(target=self.__update_playback_position_thread).start()

    def __retrive_last_boot_playback(self):
        if not path.isfile(self.__resume_file):
            # start the timer from 0
            self.__timer = Timer()
            return

        with open(self.__resume_file) as file:
            song = json.load(file)

        if song is not None:
            self.__playlist.add(song)

        # resume the timer from previous state
        try:
            self.__timer = Timer(song["position"])
        except TypeError:
            self.__timer = Timer()

    def run(self):
        self.__retrive_last_boot_playback()
        self.__timer.start()
        self.__rds_updater.run()
        self.__update_playback_position()

        for song in self.__playlist:
            if not self.__terminating:
                self.__now_playing = song
                print("storage_player playing:", song["path"])
                self.play(song)     # blocking
            else:
                return 

    def play(self, song):

        resume_time = song.get("position")
        if resume_time is not None:
            res = str(resume_time)
        else:
            res = "0"

        self.__rds_updater.set(song)
        self.__tmp_stream = None
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
        pause_sound = self.__config.get_sounds_folder()+self.__config.get_stop_sound()
        self.stream.send_signal(signal.SIGSTOP)
        self.__timer.pause()
        self.__tmp_stream = self.stream.stdout
        self.stream.stdout = subprocess.Popen(["ffmpeg", "-i", pause_sound, "-vn", "-f", "wav", "pipe:1"],
                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout

    def resume(self):
        if self.__tmp_stream is not None:
            self.stream.stdout = self.__tmp_stream
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
        self.__terminating = True
        self.__timer.stop()
        self.stream.kill()
        self.__rds_updater.stop()

    def song_name(self):
        return self.__now_playing["title"]

    def song_artist(self):
        return self.__now_playing["artist"]

    def song_year(self):
        return self.__now_playing["year"]

    def song_album(self):
        return self.__now_playing["album"]
