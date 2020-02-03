import dbus
from player import Player
import subprocess
from bytearray_io import BytearrayIO
from rds import RdsUpdater
import time
import math
import threading
import pyaudio
import wave


class BtPlayerLite(Player):

    __bt_addr = None
    __cmd_arr = None
    __rds_updater = None
    __now_playing = None
    output_stream = None
    __terminating = False
    CHUNK = None

    def __init__(self, bt_addr):
        super().__init__()
        self.update_alsa_device(bt_addr)
        self.__rds_updater = RdsUpdater()
        self.__bt_addr = bt_addr
        self.__cmd_arr = ["sudo", "dbus-send", "--system", "--type=method_call", "--dest=org.bluez", "/org/bluez/hci0/dev_"
                          + bt_addr.replace(":", "_").upper() + "/player0", "org.bluez.MediaPlayer1.Pause"]

        self.p = pyaudio.PyAudio()
        self.out_s = None

    def set_out_stream(self, outs):
        self.out_s = outs

    def playback_position(self):
        pass

    def resume(self):
        self.__cmd_arr[len(self.__cmd_arr) - 1] = "org.bluez.MediaPlayer1.Play"
        subprocess.call(self.__cmd_arr)

    def run(self):
        threading.Thread(target=self.__run).start()

    def __run(self):
        print("playing bluetooth:", self.__bt_addr)
        dev = "bluealsa:HCI=hci0,DEV="+self.__bt_addr
        self.__rds_updater.run()
        while not self.__terminating:
            self.play(dev)
            time.sleep(1)

    def update_alsa_device(self, device):
        cmd = ["sed", "-i", "s/^defaults.bluealsa.device.*$/defaults.bluealsa.device "+device+"/g", "/etc/asound.conf"]
        subprocess.call(cmd)

    def play(self, device):
        self.update_alsa_device(device)
        # open input device
        dev = None
        for i in range(self.p.get_device_count()):
            if self.p.get_device_info_by_index(i)['name'] == 'bluealsa':
                dev = self.p.get_device_info_by_index(i)

        # Consider 1 byte = 8 bit uncompressed mono signal
        # double that for a stereo signal, we get 2 bytes,
        # 16 bit stereo means 4 bytes audio frames
        in_channels = 2
        in_fmt = pyaudio.paInt16
        # 44100 frames per second means 176400 bytes per second or 1411.2 Kbps
        sample_rate = 44100

        buffer_time = 50  # 50ms audio coverage per iteration

        # How many frames to read each time. for 44100Hz 44,1 is 1ms equivalent
        frame_chunk = math.ceil(int((sample_rate / 1000) * buffer_time))

        # This will setup the stream to read CHUNK frames
        audio_stream = self.p.open(sample_rate, channels=in_channels, format=in_fmt, input=True,
                                   input_device_index=dev['index'], frames_per_buffer=frame_chunk)

        # open output stream
        self.output_stream = BytearrayIO()
        if self.out_s is not None:
            self.output_stream.set_out_stream(self.out_s)

        container = wave.open(self.output_stream, 'wb')
        container.setnchannels(in_channels)
        container.setsampwidth(self.p.get_sample_size(in_fmt))
        container.setframerate(sample_rate)

        self.ready.set()

        while not self.__terminating:
            try:
                data = audio_stream.read(frame_chunk, False)  # NB: If debugging, remove False
                container.writeframesraw(data)
            except OSError:
                self.__terminating = True
                break
                # TODO: stopping on bluetooth detach should be fully handled by the main thread

        # close output container and tell the buffer no more data is coming
        container.close()
        try:
            audio_stream.stop_stream()
        except OSError:
            pass
        audio_stream.close()
        self.p.terminate()

    def get_now_playing(self):
        try:
            bus = dbus.SystemBus()
            player = bus.get_object("org.bluez", "/org/bluez/hci0/dev_" + self.__bt_addr.replace(":", "_").upper()
                                    + "/player0")
            BT_Media_iface = dbus.Interface(player, dbus_interface="org.bluez.MediaPlayer1")
            BT_Media_probs = dbus.Interface(player, "org.freedesktop.DBus.Properties")
            probs = BT_Media_probs.GetAll("org.bluez.MediaPlayer1")

            self.__now_playing = dict()
            self.__now_playing["title"] = probs["Track"]["Title"]
            self.__now_playing["artist"] = probs["Track"]["Artist"]
            self.__now_playing["album"] = probs["Track"]["Album"]
        except dbus.DBusException:
            pass
        except KeyError:
            self.__now_playing = None

    def pause(self):
        self.__cmd_arr[len(self.__cmd_arr) - 1] = "org.bluez.MediaPlayer1.Pause"
        subprocess.call(self.__cmd_arr)

    def next(self):
        self.__cmd_arr[len(self.__cmd_arr) - 1] = "org.bluez.MediaPlayer1.Next"
        subprocess.call(self.__cmd_arr)

    def previous(self):
        self.__cmd_arr[len(self.__cmd_arr) - 1] = "org.bluez.MediaPlayer1.Previous"
        subprocess.call(self.__cmd_arr)

    def repeat(self):
        self.__cmd_arr[len(self.__cmd_arr) - 1] = "org.bluez.MediaPlayer1.Repeat"
        subprocess.call(self.__cmd_arr)

    def fast_forward(self):
        pass

    def rewind(self):
        pass

    def stop(self):
        self.output_stream.silence(True)
        self.__rds_updater.stop()
        self.__terminating = True
        time.sleep(1)
        self.output_stream.stop()
        print("bluetooth player stopped")

    def song_name(self):
        return self.__now_playing["title"]

    def song_artist(self):
        return self.__now_playing["artist"]

    def song_year(self):
        return self.__now_playing["year"]

    def song_album(self):
        return self.__now_playing["album"]

