from output import Output
import subprocess


class AnalogOutput(Output):

    def __init__(self):
        super().__init__()

    def start(self):
        self.stream = subprocess.Popen(["aplay", "-"], stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def stop(self):
        self.stream.kill()
