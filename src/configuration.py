import platform
from configparser import ConfigParser
import json


class Configuration:

    __config = None
    __pirateradio_root = "/pirateradio/"
    __sounds_folder = "/home/pi/mpradio/sounds/"        # TODO: maybe move sounds to /home/pi/sounds?
    __music_folder = ""     # to be set depending on platform
    __config_file_name = "pirateradio.config"
    __config_file_path = ""
    __resume_file = "resume.json"
    __playlist_file = "playlist.json"
    __stop_sound = "stop1.wav"
    __rds_ctl = "/tmp/rds_ctl"
    __ctl_path = "/tmp/mpradio_bt"

    def __init__(self):
        self.__config = ConfigParser()

        if platform.machine() == "x86_64":
            self.__config_file_path = "../install/pirateradio/" + self.__config_file_name
        else:
            self.__config_file_path = self.__pirateradio_root + self.__config_file_name

        self.load()

    def load(self):
        if platform.machine() == "x86_64":
            if len(self.__config.read(self.__config_file_path)) < 1:
                print("Configuration file missing:", self.__config_file_path,
                      "make sure you are running mpradio.py from src/ folder")

            # override system-specific configurations if not on a Pi
            self.__config["PIRATERADIO"]["output"] = "analog"
            self.__sounds_folder = "../sounds/"
            self.__music_folder = "../songs/"
        else:
            if len(self.__config.read(self.__config_file_path)) < 1:
                print("Configuration file missing:", self.__config_file_path,
                      "make sure you have pirateradio.config under", self.__pirateradio_root, "folder")

            self.__resume_file = self.__pirateradio_root + self.__resume_file
            self.__playlist_file = self.__pirateradio_root + self.__playlist_file
            self.__music_folder = self.__pirateradio_root

    def save(self):
        with open(self.__config_file_path, 'w') as configfile:
            self.__config.write(configfile)

    def load_json(self, configuration):
        self.__config.read_dict(json.loads(configuration))
        self.save()

    def to_json(self):
        d = dict()
        for section in dict(self.__config.items()):
            if section == "DEFAULT":
                continue
            d[section] = dict()
            for item in dict(self.__config.items(section)):
                d[section][item] = self.__config[section][item]
        return json.dumps(d)

    def get_settings(self):
        return self.__config

    def get_root(self):
        return self.__pirateradio_root

    def get_resume_file(self):
        return self.__resume_file

    def get_sounds_folder(self):
        return self.__sounds_folder

    def get_stop_sound(self):
        return self.__stop_sound

    def get_playlist_file(self):
        return self.__playlist_file

    def get_music_folder(self):
        return self.__music_folder

    def get_rds_ctl(self):
        return self.__rds_ctl

    def get_ctl_path(self):
        return self.__ctl_path


# This will be executed on first module import only
config = Configuration()
