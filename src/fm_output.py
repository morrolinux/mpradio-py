from output import Output
import subprocess
from configuration import Configuration


class FmOutput(Output):

    __config = None
    __frequency = None

    def __init__(self):
        super().__init__()
        self.__config = Configuration().get_settings()
        self.__frequency = self.__config["PIRATERADIO"]["frequency"]

    def start(self):
        self.stream = subprocess.Popen(["sudo", "pi_fm_adv", "--freq", self.__frequency, "--audio", "-"],
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def stop(self):
        self.stream.kill()
