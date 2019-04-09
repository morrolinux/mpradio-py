from output import Output
import subprocess
from configuration import Configuration
import os


class FmOutput(Output):

    __config = None
    __frequency = None
    __rds_ctl = None

    def __init__(self):
        super().__init__()
        self.__config = Configuration().get_settings()
        self.__frequency = self.__config["PIRATERADIO"]["frequency"]
        self.__rds_ctl = self.__config.get_rds_ctl()
        try:
            os.mkfifo(self.__rds_ctl)
        except FileExistsError:
            pass

    def start(self):
        print("broadcasting on FM", self.__frequency)
        self.stream = subprocess.Popen(["sudo", "pi_fm_adv", "--freq", self.__frequency,
                                        "--ctl", self.__rds_ctl, "--audio", "-"],
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def stop(self):
        self.stream.kill()
