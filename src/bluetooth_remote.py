from media import MediaInfo, MediaControl
import threading

# TODO: implement a bluetooth rfcomm remote that can communicate with the Android app


class BtRemote(MediaInfo, MediaControl):

    __event = None

    def __init__(self, event):
        super().__init__()
        self.__event = event

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
        pass

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
        pass
