from media_scanner import MediaScanner
import json
from os import path
from configuration import config
from random import randint


class Playlist:

    __queued = None
    __played = None
    __current = None
    __ms = None
    __playlist_file = None
    __resuming = False

    def __init__(self):
        self.__playlist_file = config.get_playlist_file()
        self.load_playlist()
        self.__ms = MediaScanner()
        if self.__queued is None:
            self.__queued = self.__ms.scan()
            self.save_playlist()
        self.__played = []

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.__queued) > 0:
            idx = len(self.__queued) - 1
            # pop a random song according to settings.
            # Unless another song must be resumed from previous boot
            if config.get_settings()["PLAYLIST"]["shuffle"] == "true" and not self.__resuming:
                idx = randint(0, len(self.__queued) - 1)
            self.__resuming = False
            self.__current = self.__queued.pop(idx)
            self.__played.append(self.__current)
        else:
            self.__queued = self.__ms.scan()
            self.__current = self.__queued.pop()        # TODO: handle the "no songs" scenario
            self.__played.append(self.__current)

        print("\n\nplaylist:", [song["path"] for song in self.__queued], "\n")
        print("played:", [song["path"] for song in self.__played], "\n\n")
        self.save_playlist()

        return self.__current

    def save_playlist(self):
        with open(self.__playlist_file, "w") as f:
            j = json.dumps(self.__queued)
            f.write(j)

    def load_playlist(self):
        if not path.isfile(self.__playlist_file):
            return
        with open(self.__playlist_file) as file:
            self.__queued = json.load(file)

    def back(self, n=0):
        for _ in range(n+1):
            try:
                s = self.__played.pop()
                s["position"] = "0"
                self.__queued.append(s)
            except IndexError:
                print("no songs left in playback history")

    def elements(self):
        return self.__queued

    def current(self):
        return self.__current

    def add(self, song):
        self.__queued.append(song)

    def set_resuming(self):
        self.__resuming = True
