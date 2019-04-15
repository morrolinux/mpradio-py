from media import MediaInfo, MediaControl
from subprocess import call
import threading
import bluetooth

# TODO: implement a bluetooth rfcomm remote that can communicate with the Android app


class BtRemote(MediaInfo, MediaControl):

    __event = None
    __msg = None
    __server_socket = None
    __port = 1
    __termination = None

    def __init__(self, event, message):
        super().__init__()
        self.__event = event
        self.__msg = message
        call(["sudo", "sdptool", "add", "SP"])
        self.__server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.__termination = threading.Event()

    def song_name(self):
        pass

    def song_artist(self):
        pass

    def song_year(self):
        pass

    def song_album(self):
        pass

    def run(self):
        threading.Thread(target=self.__run).start()

    def __run(self):
        self.__server_socket.bind(("", bluetooth.PORT_ANY))     # or simply use self.__port
        self.__server_socket.listen(1)
        port = self.__server_socket.getsockname()[1]            # or simply use self.__port
        uuid = "00001101-0000-1000-8000-00805f9b34fb"           # android app looks for this

        bluetooth.advertise_service(self.__server_socket, "MPRadio",
                                    service_id=uuid,
                                    service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                                    profiles=[bluetooth.SERIAL_PORT_PROFILE],)

        while not self.__termination.is_set():
            client_sock, address = self.__server_socket.accept()
            cmd = client_sock.recv(1024)

            if len(cmd) > 0:
                cmd = cmd.decode().strip().lower().split()
                self.__msg["command"] = cmd
                self.__msg["source"] = "bluetooth"
                self.__event.set()

            client_sock.close()

        self.__server_socket.close()

    def resume(self):
        pass

    def pause(self):
        pass

    def next(self):
        pass

    def previous(self):
        pass

    def repeat(self):
        pass

    def fast_forward(self):
        pass

    def rewind(self):
        pass

    def stop(self):
        self.__termination.set()
