import subprocess
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK
from configuration import config
import threading
import time


class Encoder:

    stream = None
    __sox_compression = ["compand", "0.3,1", "6:-70,-60,-20", "-5", "-90", "0.2"]
    __compression_supported_models = ("Pi 3", "Pi 2")
    input_stream = None
    output_stream = None
    ready = threading.Event()

    def __init__(self):
        self.__sox_cmd = ["sox", "-t", "raw", "-G", "-b", "16", "-e", "signed",
                          "-c", "2", "-r", "44100", "-", "-t", "wav", "-"]
        self.__enable_compression_if_supported()
        self.__set_treble()

    def run(self):
        self.stream = subprocess.Popen(self.__sox_cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                       stderr=subprocess.PIPE)    # -1
        # set the encoder to non-blocking output:
        flags = fcntl(self.stream.stdout, F_GETFL)  # get current stdout flags
        fcntl(self.stream.stdout, F_SETFL, flags | O_NONBLOCK)
        self.input_stream = self.stream.stdin
        self.output_stream = self.stream.stdout
        time.sleep(2)   # TODO: find a better way to determine if the process is ready
        self.ready.set()

    def reload(self):
        self.ready.clear()
        self.stop()
        self.__init__()
        self.run()

    def stop(self):
        self.stream.kill()

    def __enable_compression_if_supported(self):
        try:
            with open("/sys/firmware/devicetree/base/model") as f:
                model = f.read()
                for supp in self.__compression_supported_models:
                    if supp in model:
                        self.__sox_cmd.extend(self.__sox_compression)
        except FileNotFoundError:
            pass

    def __set_treble(self):
        treble = config.get_settings()["PIRATERADIO"]["treble"]
        if treble != "0":
            self.__sox_cmd.extend(["treble", treble])
