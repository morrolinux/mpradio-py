from player import Player
import subprocess
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK
import threading


class BtPlayer(Player):

    __bt_addr = None
    __cmd_arr = None

    def __init__(self, bt_addr):
        super().__init__()
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
        self.stream = subprocess.Popen(["arecord", "-D", dev, "-f", "cd", "-c", "2"],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # set the player to non-blocking output:
        flags = fcntl(self.stream.stdout, F_GETFL)  # get current stdout flags
        fcntl(self.stream.stdout, F_SETFL, flags | O_NONBLOCK)

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
        self.stream.kill()
        print("bluetooth player stopped")

    def song_name(self):
        pass

    def song_artist(self):
        pass

    def song_year(self):
        pass

    def song_album(self):
        pass

