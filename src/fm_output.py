from output import Output
import subprocess


class FmOutput(Output):

    def __init__(self):
        super().__init__()

    def start(self):
        self.stream = subprocess.Popen(["sudo", "pi_fm_adv", "--audio", "-"], stdin=subprocess.PIPE)

    def stop(self):
        pass

