import os

from mutagen.easyid3 import EasyID3

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

                    fallback_title = f
                    for curr_format in self.supported_formats:
                        fallback_title = fallback_title.replace("."+ curr_format,"")
                    tmp["title"] = fallback_title

                    tmp["artist"] = None
                    tmp["album"] = None
                    tmp["year"] = None

                    audio_id3 = EasyID3(tmp["path"])
                    for key in tmp:
                        if key in audio_id3 and len(audio_id3[key]) > 0:
                            tmp[key] = audio_id3[key][0]     
                    self.__songs.append(tmp)
        return self.__songs