from media import MediaInfo, MediaControl
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
        self.__server_socket.bind(("", bluetooth.PORT_ANY))
        self.__server_socket.listen(1)
        port = self.__server_socket.getsockname()[1]
        # uuid = "f3c74f47-1d38-49ed-8bbc-0369b3eb277c"
        uuid = "F9EC7BC4-953C-11D2-984E-525400DC9E09"   # android side

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
