import platform
from configparser import ConfigParser


class Configuration:

    __config = None
    __config_file_name = "pirateradio.config"
    __pirateradio_root = "/pirateradio/"

    def __init__(self):
        self.__config = ConfigParser()

        if platform.machine() == "x86_64":
            if len(self.__config.read("../install/"+self.__config_file_name)) < 1:
                print("Configuration file missing:" + self.__config_file_name)
                print("make sure you are running mpradio.py from src/ folder")

            # override system-specific configurations if not on a Pi
            self.__config["PIRATERADIO"]["output"] = "analog"
        else:
            if len(self.__config.read(self.__pirateradio_root+self.__config_file_name)) < 1:
                print("Configuration file missing:"+self.__config_file_name)
                print("make sure you have pirateradio.config under "+self.__pirateradio_root+" folder")

    def get_settings(self):
        return self.__config

    def get_root(self):
        return self.__pirateradio_root
