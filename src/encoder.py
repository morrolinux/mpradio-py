import subprocess
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK
from configuration import config


class Encoder:

    stream = None
    __sox_cmd = ["sox", "-t", "raw", "-G", "-b", "16", "-e", "signed",
                 "-c", "2", "-r", "44100", "-", "-t", "wav", "-"]
    # __sox_treble = ["treble", "-6"]
    __sox_compression = ["compand", "0.3,1", "6:-70,-60,-20", "-5", "-90", "0.2"]

    def __init__(self):
        # self.__sox_cmd.extend(self.__sox_compression)
        treble = config.get_settings()["PIRATERADIO"]["treble"]
        if treble != "0":
            self.__sox_cmd.extend(["treble", treble])

    def run(self):
        self.stream = subprocess.Popen(self.__sox_cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                       stderr=subprocess.PIPE, bufsize=0)    # -1
        # set the encoder to non-blocking output:
        flags = fcntl(self.stream.stdout, F_GETFL)  # get current stdout flags
        fcntl(self.stream.stdout, F_SETFL, flags | O_NONBLOCK)

    def stop(self):
        self.stream.kill()
