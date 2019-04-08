import os
import platform


class MediaScanner:

    supported_formats = ("mp3", "m4a", "wav", "flac", "ogg")
    __songs = None

    def __init__(self):
        # TODO: read ini configuration here
        self.__songs = []

    def scan(self, path=None):
        if path is None:
            if platform.machine() == "x86_64":
                path = os.getcwd()+"/../songs"
            else:
                path = "/home/pi/"      # TODO: set scan path from configuration

        for root, d_names, f_names in os.walk(path):
            for f in f_names:
                if f.endswith(self.supported_formats):
                    tmp = dict()
                    tmp["path"] = root+"/"+f
                    tmp["title"] = f     # TODO: fill-in id3 tags
                    tmp["artist"] = "song artist"
                    tmp["album"] = "song album"
                    tmp["year"] = "song year"
                    self.__songs.append(tmp)
        return self.__songs
