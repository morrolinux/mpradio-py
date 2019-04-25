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
    __skip = None
    __play_lock = None
    __out = None

    def __init__(self):
        super().__init__()
        self.__playlist = Playlist()
        self.__rds_updater = RdsUpdater()
        self.__resume_file = config.get_resume_file()
        self.__skip = threading.Event()
        self.__play_lock = threading.Lock()

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
            self.play_on_demand(song)
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

    def play_on_demand(self, song):
        self.enqueue(song)
        self.next()

    def enqueue(self, song):
        self.__playlist.add(song)
        self.__playlist.set_noshuffle()

    def play(self, song):
        # tell other storage player thread to terminate; acquire lock; cleanup
        self.__skip.set()
        self.__play_lock.acquire()
        self.__skip.clear()
        self._tmp_stream = None

        # get/set/resume song timer
        resume_time = song.get("position")
        if resume_time is None:
            resume_time = 0
            self.__timer.reset()
        self.__timer.resume()

        # update song name
        self.__now_playing = song
        self.__rds_updater.set(song)
        song_path = r"" + song["path"].replace("\\", "")

        # open input file
        try:
            input_container = av.open(song_path)
            audio_stream = None
            for i, stream in enumerate(input_container.streams):
                if stream.type == 'audio':
                    audio_stream = stream
                    break
            if not audio_stream:
                self.__player_clean_termination()
                return
        except av.AVError:
            print("Can't open file:", song_path, "skipping...")
            self.__player_clean_termination()
            return

        # open output stream
        self.__out = MpradioIO()
        self.output_stream = self.__out       # link for external access
        out_container = av.open(self.__out, 'w', 'wav')
        out_stream = out_container.add_stream(codec_name='pcm_s16le', rate=44100)

        # calculate initial seek
        time_unit = input_container.size/int(input_container.duration/1000000)
        seek_point = time_unit * resume_time

        # transcode input to wav
        for i, packet in enumerate(input_container.demux(audio_stream)):
            # seek to the point
            try:
                if packet.pos < seek_point:
                    continue
            except TypeError:
                pass

            try:
                for frame in packet.decode():
                    frame.pts = None
                    out_pack = out_stream.encode(frame)
                    if out_pack:
                        out_container.mux(out_pack)
            except av.AVError:
                print("Error during playback for:", song_path)
                self.__player_clean_termination()
                return

            # stop transcoding if we receive skip or termination signal
            if self.__terminating or self.__skip.is_set():
                break

            # set the player to ready after a short buffer is ready
            if not self.ready.is_set():
                try:
                    if packet.pos > resume_time + time_unit*2:
                        self.ready.set()
                except TypeError:
                    pass

            # avoid CPU saturation on single-core systems
            if psutil.cpu_percent() > 90:
                time.sleep(0.02)

        # transcoding terminated. Flush output stream
        while True:
            out_pack = out_stream.encode(None)
            if out_pack:
                out_container.mux(out_pack)
            else:
                break

        # close output container and tell the buffer no more data is coming
        out_container.close()
        self.__out.set_write_completed()
        print("transcoding finished.")

        # wait until playback (buffer read) terminates; catch signals meanwhile
        while not self.__out.is_read_completed():
            if self.__skip.is_set():
                self.__skip.clear()
                break
            if self.__terminating:
                break
            time.sleep(0.2)

        # clear flags and release locks
        self.__player_clean_termination()

    def __player_clean_termination(self):
        self.__skip.clear()
        self.__play_lock.release()

    def pause(self):
        if self.__timer.is_paused():
            return
        self.__timer.pause()
        self.silence()

    def resume(self):
        if self._tmp_stream is not None:
            self.output_stream = self._tmp_stream
        self.__timer.resume()

    def next(self):
        self.__skip.set()

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
