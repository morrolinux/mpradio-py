from os import path
import time
from timer import Timer
from player import Player
from playlist import Playlist
from rds import RdsUpdater
import threading
import json
from configuration import config
import psutil
import av
from mp_io import MpradioIO


class StoragePlayer(Player):

    __terminating = False
    __playlist = None
    __now_playing = None
    __timer = None
    __resume_file = None
    __rds_updater = None
    __ready = False
    __skip = False
    out = None

    def __init__(self):
        super().__init__()
        self.__playlist = Playlist()
        self.__rds_updater = RdsUpdater()
        self.__resume_file = config.get_resume_file()

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
            self.__playlist.set_resuming()

        # resume the timer from previous state
        try:
            self.__timer = Timer(song["position"])
        except TypeError:
            self.__timer = Timer()

    def run(self):
        threading.Thread(target=self.__run).start()

    def __run(self):
        self.__retrive_last_boot_playback()
        self.__timer.start()
        self.__rds_updater.run()
        self.__update_playback_position()

        for song in self.__playlist:
            print("storage_player playing:", song["path"])
            self.play(song)     # blocking
            if self.__terminating:
                return

    def play(self, song):
        # print("player received:", song)
        self.__now_playing = song

        resume_time = song.get("position")
        if resume_time is None:
            resume_time = 0
            self.__timer.reset()

        self.__rds_updater.set(song)
        self._tmp_stream = None             # TODO: remove unneeded?
        song_path = r"" + song["path"].replace("\\", "")

        # input file
        container = av.open(song_path)
        audio_stream = None
        for i, stream in enumerate(container.streams):
            if stream.type == 'audio':
                audio_stream = stream
                break
        if not audio_stream:
            return

        # output stream
        self.out = MpradioIO()   # TODO: replace with something more generic like "output"
        out_container = av.open(self.out, 'w', 'wav')
        out_stream = out_container.add_stream(codec_name='pcm_s16le', rate=44100)
        for i, packet in enumerate(container.demux(audio_stream)):
            for frame in packet.decode():
                frame.pts = None
                out_pack = out_stream.encode(frame)
                if out_pack:
                    out_container.mux(out_pack)

            # set the player to ready after a short buffer is ready
            if i == 10:
                self.__ready = True

            # avoid CPU saturation on single-core systems
            if psutil.cpu_percent() > 90:
                time.sleep(0.02)

            if self.__skip:
                break

            # exit and flushing
            # if i > 500:
            #     while True:
            #         out_pack = out_stream.encode(None)
            #         if out_pack:
            #             # print(out_pack.pts)
            #             out_container.mux(out_pack)
            #         else:
            #             break
            #     break
        out_container.close()
        self.out.set_write_completed()
        print("transcode finished.")

        # Wait until playback (buffer read) terminates
        while not self.out.is_read_completed():
            if self.__skip:
                self.__skip = False
                return
            time.sleep(0.2)

    def pause(self):
        if self.__timer.is_paused():
            return
        self.__timer.pause()
        self.silence()

    def resume(self):
        if self._tmp_stream is not None:
            self.out = self._tmp_stream
        self.__timer.resume()

    def next(self):
        self.__skip = True
        # self.silence()

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
        self.silence()
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

    def is_ready(self):
        return self.__ready
