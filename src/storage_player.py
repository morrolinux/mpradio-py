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
    __out = None
    __silence_track = None
    __tmp_stream = None

    def __init__(self):
        super().__init__()
        self.__playlist = Playlist()
        self.__rds_updater = RdsUpdater()
        self.__resume_file = config.get_resume_file()
        self.__skip = threading.Event()
        self.output_stream = None

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
        self.__retrive_last_boot_playback()
        self.__timer.start()
        self.__rds_updater.run()
        self.__update_playback_position()
        self.__generate_silence()

        for song in self.__playlist:
            if song is None:
                return
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
        # cleanup and generate silence for pi_fm_adv so it won't stutter
        self.silence()
        self.__tmp_stream = None

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

        # create output stream
        self.__out = MpradioIO()
        out_container = av.open(self.__out, 'w', 'wav')
        out_stream = out_container.add_stream(codec_name='pcm_s16le', rate=44100)

        # calculate initial seek
        try:
            time_unit = input_container.size/int(input_container.duration/1000000)
        except ZeroDivisionError:
            time_unit = 0
        seek_point = time_unit * resume_time

        buffer_ready = False

        # transcode input to wav
        for packet in input_container.demux(audio_stream):

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
                    if packet.pos > resume_time + time_unit*2:
                        self.output_stream = self.__out  # link for external access
                        self.ready.set()
                        buffer_ready = True
                except TypeError:
                    pass

            # avoid CPU saturation on single-core systems
            if psutil.cpu_percent() > 95:
                time.sleep(0.01)

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

    def __generate_silence(self):
        self.__silence_track = MpradioIO()
        out_container = av.open(self.__silence_track, 'w', 'wav')
        out_stream = out_container.add_stream(codec_name='pcm_s16le', rate=44100)

        # open input file
        try:
            input_container = av.open(config.get_sounds_folder() + config.get_stop_sound())
            audio_stream = input_container.streams[0]
        except av.AVError:
            print("Can't open silence file, skipping...")
            return

        # transcode input to wav
        for packet in input_container.demux(audio_stream):
            try:
                for frame in packet.decode():
                    frame.pts = None
                    out_pack = out_stream.encode(frame)
                    if out_pack:
                        out_container.mux(out_pack)
            except av.AVError:
                print("Error during playback for:", song_path)
                return

        out_container.close()
        self.__silence_track.set_write_completed()

    def silence(self):
        """
            This will backup the player output_stream and replace it with a dummy stream containing silence.
            The original output stream must then be swapped back for the player to be read from external again.
            We need this because pi_fm_adv for FM output will loop-stutter if input stops.
        """
        self.__tmp_stream = self.output_stream
        self.__silence_track.seek_to_start()
        self.output_stream = self.__silence_track

    def pause(self):
        if self.__timer.is_paused():
            return
        self.__timer.pause()
        self.silence()

    def resume(self):
        if not self.__timer.is_paused():
            return
        self.output_stream = self.__tmp_stream
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
        self.__terminating = True
        self.silence()
        self.ready.clear()
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
