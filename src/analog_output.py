from output import Output
import subprocess


class AnalogOutput(Output):

    def __init__(self):
        super().__init__()

    def run(self):
        self.stream = subprocess.Popen(["aplay", "-"], stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.input_stream = self.stream.stdin
        self.output_stream = self.stream.stdout

    def stop(self):
        self.stream.kill()

    def check_reload(self):
        pass
