import os
from mutagen.id3 import ID3NoHeaderError
from configuration import config
from mutagen.easyid3 import EasyID3


class MediaScanner:

    supported_formats = ("mp3", "m4a", "wav", "flac", "ogg")
    __songs = None

    def __init__(self):
        self.__songs = []

    def scan(self, path=None):
        if path is None:
            path = config.get_music_folder()

        for root, d_names, f_names in os.walk(path):
            for f in f_names:
                if f.endswith(self.supported_formats):
                    tmp = dict()
                    tmp["path"] = os.path.join(root, f).replace(" ", "\\ ")
                    fallback_title = f
                    for curr_format in self.supported_formats:
                        fallback_title = fallback_title.replace("." + curr_format, "")
                    tmp["title"] = fallback_title

                    # Avoid "can only concatenate str (not "NoneType") to str" error everywhere
                    # default empty string will do just fine.
                    tmp["artist"] = ""
                    tmp["album"] = os.path.basename(os.path.dirname(path))
                    tmp["year"] = ""

                    # Otherwise The application will crash if no id3 header is present
                    try:
                        audio_id3 = EasyID3(tmp["path"])
                        for key in tmp:
                            if key in audio_id3 and len(audio_id3[key]) > 0:
                                tmp[key] = audio_id3[key][0]
                    except ID3NoHeaderError:
                        pass

                    self.__songs.append(tmp)

        return self.__songs
