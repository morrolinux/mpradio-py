import threading
import time
import platform
from configuration import config


class RdsUpdater:

    __interval = None
    __termination = None
    __song = None
    __step = None
    __output = None
    __rds_ctl = None
    __updated = False
    __pattern = None

    def __init__(self):
        self.__termination = threading.Event()
        self.__rds_ctl = config.get_rds_ctl()

        if platform.machine() == "x86_64":
            self.__output = print
        else:
            self.__output = self.write_rds_to_pipe

        self.__interval = int(config.get_settings()["RDS"]["updateInterval"])
        self.__step = int(config.get_settings()["RDS"]["charsJump"])
        self.__pattern = config.get_settings()["RDS"]["rdsPattern"]

    def set(self, song):
        if song != self.__song:
            self.__song = song
            self.__updated = True

    def write_rds_to_pipe(self, text):
        with open(self.__rds_ctl, "w") as f:
            text = text.strip() + "\n"
            f.write("RT "+text)

    def __format_song(self):
        """Format the song string based on the configured pattern"""
        pattern = self.__pattern
        
        # Replace pattern variables with actual song values
        pattern = pattern.replace("$SONG_NAME", self.__song.get("title", "Unknown"))
        pattern = pattern.replace("$ARTIST_NAME", self.__song.get("artist", "Unknown"))
        pattern = pattern.replace("$ALBUM_NAME", self.__song.get("album", "Unknown"))
        pattern = pattern.replace("$YEAR", self.__song.get("year", "Unknown"))
        pattern = pattern.replace("$GENRE", self.__song.get("genre", "Unknown"))
        pattern = pattern.replace("$DURATION", self.__song.get("duration", "Unknown"))
        pattern = pattern.replace("$BITRATE", self.__song.get("bitrate", "Unknown"))

     return pattern

    def __run(self):
        while not self.__termination.is_set():
            # wait for the song to be set.
            if self.__song is None:
                time.sleep(0.2)
                continue

            formatted_song = self.__format_song()
            for qg in self.q_gram(formatted_song):
                
                self.__output(qg)
                if self.__termination.is_set():
                    return
                if self.__updated:
                    self.__updated = False
                    break
                time.sleep(self.__interval)

    # print q-grams of the given title
    def q_gram(self, text):
        q = []

        if len(text) < 65:
            q.append(text)
            return q

        for i in range(0, len(text), self.__step):
            start = i
            end = i + 64
            if end > len(text):
                break
            s = text[start:end]
            q.append(s)
        return q

    def run(self):
        threading.Thread(target=self.__run).start()

    def stop(self):
        self.__termination.set()
