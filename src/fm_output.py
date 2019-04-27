from output import Output
import subprocess
from configuration import config
from subprocess import call
import os


class FmOutput(Output):

    __frequency = None
    __rds_ctl = None

    def __init__(self):
        super().__init__()
        self.__frequency = config.get_settings()["PIRATERADIO"]["frequency"]
        self.__rds_ctl = config.get_rds_ctl()
        try:
            os.mkfifo(self.__rds_ctl)
        except FileExistsError:
            pass

    def run(self):
        print("broadcasting on FM", self.__frequency)
        self.stream = subprocess.Popen(["sudo", "pi_fm_adv", "--freq", self.__frequency,
                                        "--ctl", self.__rds_ctl, "--audio", "-"],
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.input_stream = self.stream.stdin
        self.output_stream = self.stream.stdout

    def stop(self):
        call(["sudo", "kill", str(self.stream.pid)])

    def reload(self):
        self.stop()
        self.__init__()
        self.run()
