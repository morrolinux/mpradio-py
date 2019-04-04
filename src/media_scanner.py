import os


class MediaScanner:

    supported_formats = ("mp3", "m4a", "wav", "flac", "ogg")
    __songs = None

    def __init__(self):
        # TODO: read ini configuration here
        self.__songs = []

    def scan(self, path=None):
        if path is None:
            path = os.getcwd()+"/../"   # TODO: set scan path from configuration

        for root, d_names, f_names in os.walk(path):
            for f in f_names:
                if f.endswith(self.supported_formats):
                    tmp = dict()
                    tmp["path"] = root+"/"+f
                    tmp["title"] = "title"    # TODO: fill-in id3 tags
                    tmp["artist"] = "artist"
                    tmp["album"] = "album"
                    tmp["year"] = "year"
                    self.__songs.append(tmp)
        return self.__songs
