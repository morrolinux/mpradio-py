import dbus
from player import Player
import subprocess
import av
from mp_io import MpradioIO
from rds import RdsUpdater
import time
import threading


class BtPlayer(Player):

    __bt_addr = None
    __cmd_arr = None
    __rds_updater = None
    __now_playing = None
    output_stream = None
    __terminating = False
    CHUNK = 1024 * 2

    def __init__(self, bt_addr):
        super().__init__()
        self.__rds_updater = RdsUpdater()
        self.__bt_addr = bt_addr
        self.__cmd_arr = ["sudo", "dbus-send", "--system", "--type=method_call", "--dest=org.bluez", "/org/bluez/hci0/dev_"
                          + bt_addr.replace(":", "_").upper() + "/player0", "org.bluez.MediaPlayer1.Pause"]

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
        try:
            input_container = av.open(device, format="alsa")

            audio_stream = None
            for i, stream in enumerate(input_container.streams):
                if stream.type == 'audio':
                    audio_stream = stream
                    break

            if not audio_stream:
                print("audio stream not found")
                return

        except av.AVError:
            print("Can't open input stream for device", device)
            return

        # open output stream
        self.output_stream = MpradioIO()
        out_container = av.open(self.output_stream, 'w', 'wav')
        out_stream = out_container.add_stream(codec_name='pcm_s16le', rate=44100)

        # transcode input to wav
        for i, packet in enumerate(input_container.demux(audio_stream)):
            try:
                for frame in packet.decode():
                    frame.pts = None
                    out_pack = out_stream.encode(frame)
                    if out_pack:
                        out_container.mux(out_pack)
                    else:
                        print("out_pack is None")
            except av.AVError:
                print("Error during playback for:", device)
                return

            # stop transcoding if we receive termination signal
            if self.__terminating:
                print("termination signal received")
                break

            # pre-buffer
            if i == 4:
                self.ready.set()

            # Avoid CPU saturation on single-core systems.
            # time.sleep(0.001)

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
        self.output_stream.set_write_completed()
        print("transcoding finished.")

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
        print("bluetooth player stopped")

    def song_name(self):
        return self.__now_playing["title"]

    def song_artist(self):
        return self.__now_playing["artist"]

    def song_year(self):
        return self.__now_playing["year"]

    def song_album(self):
        return self.__now_playing["album"]

