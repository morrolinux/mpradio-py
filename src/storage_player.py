import subprocess
import signal
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK
import time
from player import Player
from playlist import Playlist


class StoragePlayer(Player):

    __tmp_out = None
    __terminating = False
    __playlist = None
    __now_playing = None

    def __init__(self):
        super().__init__()
        self.__playlist = Playlist()

    def playback_position(self):
        pass

    def run(self):
        for song in self.__playlist:
            if not self.__terminating:
                self.__now_playing = song
                print("playing:", song["path"])
                print("playlist:", [song["path"] for song in self.__playlist.elements()])
                print("........................")
                self.play(song["path"])

    def play(self, song):
        self.__tmp_out = None
        self.stream = subprocess.Popen(["ffmpeg", "-i", song, "-vn", "-f", "wav", "pipe:1"],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # set the player to non-blocking output:
        flags = fcntl(self.stream.stdout, F_GETFL)  # get current stdout flags
        fcntl(self.stream.stdout, F_SETFL, flags | O_NONBLOCK)
        # Wait until process terminates
        while self.stream.poll() is None:
            time.sleep(0.02)

    def pause(self):
        self.stream.send_signal(signal.SIGSTOP)
        self.__tmp_out = self.stream.stdout
        self.stream.stdout = subprocess.Popen(["ffmpeg", "-i", "sounds/stop1.wav", "-vn", "-f", "wav", "pipe:1"],
                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout

    def resume(self):
        if self.__tmp_out is not None:
            self.stream.stdout = self.__tmp_out
        self.stream.send_signal(signal.SIGCONT)

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

    def song_name(self):
        return self.__now_playing["title"]

    def song_artist(self):
        return self.__now_playing["artist"]

    def song_year(self):
        return self.__now_playing["year"]

    def song_album(self):
        return self.__now_playing["album"]
