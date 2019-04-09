import subprocess
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK


class Encoder:

    stream = None

    def __init__(self):
        pass
        # TODO: read from settings

    def run(self):
        self.stream = subprocess.Popen(["sox", "-t", "raw", "-G", "-b", "16", "-e", "signed",
                                        "-c", "2", "-r", "44100", "-", "-t", "wav", "-"],
                                       stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                       stderr=subprocess.PIPE, bufsize=0)    # -1
        # set the encoder to non-blocking output:
        flags = fcntl(self.stream.stdout, F_GETFL)  # get current stdout flags
        fcntl(self.stream.stdout, F_SETFL, flags | O_NONBLOCK)

    def stop(self):
        self.stream.kill()
