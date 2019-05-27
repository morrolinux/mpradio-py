import dbus
from player import Player
import subprocess
import av
from mp_io import MpradioIO
from rds import RdsUpdater
import time
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
    CHUNK = 1024 * 64   # Pi0 on integrated bluetooth seem to work best with 64k chunks

    def __init__(self, bt_addr):
        super().__init__()
        self.__rds_updater = RdsUpdater()
        self.__bt_addr = bt_addr
        self.__cmd_arr = ["sudo", "dbus-send", "--system", "--type=method_call", "--dest=org.bluez", "/org/bluez/hci0/dev_"
                          + bt_addr.replace(":", "_").upper() + "/player0", "org.bluez.MediaPlayer1.Pause"]

        self.p = pyaudio.PyAudio()

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

    def play(self, device):
        # open input device
        dev = None
        for i in range(self.p.get_device_count()):
            if self.p.get_device_info_by_index(i)['name'] == 'bluealsa':
                dev = self.p.get_device_info_by_index(i)

        sample_rate = int(dev['defaultSampleRate'])
        in_channels = 2
        in_fmt = pyaudio.paInt16
        CHUNK = 64

        audio_stream = self.p.open(sample_rate, channels=in_channels, format=in_fmt, input=True,
                                   input_device_index=dev['index'], frames_per_buffer=CHUNK)

        # open output stream
        self.output_stream = MpradioIO()
        container = wave.open(self.output_stream, 'wb')
        container.setnchannels(2)
        container.setsampwidth(self.p.get_sample_size(in_fmt))
        container.setframerate(sample_rate)

        self.ready.set()

        while not self.__terminating:
            data = audio_stream.read(CHUNK)
            container.writeframesraw(data)

        # close output container and tell the buffer no more data is coming
        container.close()
        audio_stream.stop_stream()
        audio_stream.close()
        self.p.terminate()

        self.output_stream.set_write_completed()

        # TODO: check if this and the above is really needed when playing a device
        # wait until playback (buffer read) terminates; catch signals meanwhile
        while not self.output_stream.is_read_completed():
            if self.__terminating:
                break
            time.sleep(0.2)

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

