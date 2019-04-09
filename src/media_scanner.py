import os
from configuration import Configuration


class MediaScanner:

    supported_formats = ("mp3", "m4a", "wav", "flac", "ogg")
    __songs = None
    __config = None

    def __init__(self):
        self.__songs = []
        self.__config = Configuration()

    def scan(self, path=None):
        if path is None:
            path = self.__config.get_music_folder()

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
