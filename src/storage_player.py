from os import path
import time
from timer import Timer
from player import Player
from playlist import Playlist
from rds import RdsUpdater
import threading
import json
from configuration import config
import av
from mp_io import MpradioIO
from bytearray_io import BytearrayIO


class StoragePlayer(Player):

    __terminating = False
    __playlist = None
    __now_playing = None
    __timer = None
    __resume_file = None
    __rds_updater = None
    __skip = None
    __out = None
    __silence_track = None
    CHUNK = 1024 * 4

    def __init__(self):
        super().__init__()
        self.__playlist = Playlist()
        self.__rds_updater = RdsUpdater()
        self.__resume_file = config.get_resume_file()
        self.__skip = threading.Event()
        self.output_stream = BytearrayIO()

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

    def __retrieve_last_boot_playback(self):
        if not path.isfile(self.__resume_file):
            # start the timer from 0
            self.__timer = Timer()
            return

        try:
            with open(self.__resume_file) as file:
                song = json.load(file)
        except json.decoder.JSONDecodeError:
            self.__timer = Timer()
            return

        if song is not None:
            # resume the timer from previous state
            try:
                self.__timer = Timer(song["position"])
                self.enqueue(song)
            except TypeError:
                self.__timer = Timer()
            except KeyError:
                self.__timer = Timer()
        else:
            self.__timer = Timer()

    def run(self):
        threading.Thread(target=self.__run).start()

    def __run(self):
        self.__retrieve_last_boot_playback()
        self.__timer.start()
        self.__rds_updater.run()
        self.__update_playback_position()

        for song in self.__playlist:
            if song is None:
                time.sleep(1)
                continue
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

    def set_out_stream(self, outs):
        if outs is not None:
            self.output_stream.set_out_stream(outs, 150)

    def play(self, song):
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
                return
        except av.AVError:
            print("Can't open file:", song_path, "skipping...")
            return

        # set-up output stream
        self.output_stream.seek_to_start()
        out_container = av.open(self.output_stream, 'w', 'wav')
        out_stream = out_container.add_stream(codec_name='pcm_s16le', rate=44100)

        # calculate initial seek
        try:
            time_unit = input_container.size/int(input_container.duration/1000000)
        except ZeroDivisionError:
            time_unit = 0
        seek_point = int(time_unit) * int(resume_time)

        buffer_ready = False

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
            except av.AVError as err:
                print("Error during playback for:", song_path, err)
                return

            # stop transcoding if we receive skip or termination signal
            if self.__terminating or self.__skip.is_set():
                break

            # pre-buffer some output and set the player to ready
            if not buffer_ready:
                try:
                    if packet.pos > resume_time + time_unit * 2:
                        self.ready.set()
                        buffer_ready = True
                except TypeError:
                    pass

        # transcoding terminated. Flush output stream
        try:
            while True:
                out_pack = out_stream.encode(None)
                if out_pack:
                    out_container.mux(out_pack)
                else:
                    break
        except ValueError:
            print("skipping flush...")
            return

        # close output container and tell the buffer no more data is coming
        del input_container
        out_container.close()
        self.output_stream.set_write_completed()
        print("transcoding finished.")

        while not self.output_stream.is_read_completed():
            time.sleep(0.01)
            if self.__skip.is_set():
                self.__skip.clear()
                break

    def pause(self):
        if self.__timer.is_paused():
            return
        self.__timer.pause()
        self.output_stream.silence(True)

    def resume(self):
        if not self.__timer.is_paused():
            return
        self.output_stream.silence(False)
        self.__timer.resume()
        self.ready.set()

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
        self.output_stream.silence(True)
        self.__terminating = True
        self.__timer.stop()
        self.__rds_updater.stop()
        time.sleep(1)
        self.ready.clear()
        self.output_stream.stop()

    def song_name(self):
        return self.__now_playing["title"]

    def song_artist(self):
        return self.__now_playing["artist"]

    def song_year(self):
        return self.__now_playing["year"]

    def song_album(self):
        return self.__now_playing["album"]
