from output import Output
import subprocess


class FmOutput(Output):

    def __init__(self):
        super().__init__()
        # TODO: read from settings

    def start(self):
        self.stream = subprocess.Popen(["sudo", "pi_fm_adv", "--audio", "-"],
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def stop(self):
        self.stream.kill()
