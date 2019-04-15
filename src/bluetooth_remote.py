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
        self.__server_socket.bind(("", self.__port))
        
        while not self.__termination.is_set():
            self.__server_socket.listen(1)

            client_sock, address = self.__server_socket.accept()
            print("Accepted connection from ", address)

            data = client_sock.recv(1024)
            print("received [%s]" % data)

            if len(data) > 0:
                self.__msg["command"] = data
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
