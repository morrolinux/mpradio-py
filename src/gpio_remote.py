from media import MediaControl
import threading

# TODO: implement a GPIO remote for the push button (@DavidM42 did something already)


class GpioRemote(MediaControl):

    def run(self):
        pass

    def __run(self):
        threading.Thread(target=self.run).start()

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
