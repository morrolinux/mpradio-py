import subprocess
import os
import time


class BluetoothDaemon:

    def __init__(self):
        self.bt_setup()
        self.run_bluealsa()
        self.run_simple_agent()

    def run_simple_agent(self):
        subprocess.Popen(["sudo", "killall", "simple-agent"]).wait(5)
        simpleagent = subprocess.Popen(["sudo", "simple-agent"])

    def run_bluealsa(self):
        subprocess.Popen(["sudo", "killall", "bluealsa"]).wait(5)
        bluealsa = subprocess.Popen(["sudo", "bluealsa", "-p", "a2dp-sink", "--a2dp-force-audio-cd"])

    def bt_setup(self):
        subprocess.Popen(["sudo", "hciconfig", "hci0", "up"])
        subprocess.Popen(["sudo", "hciconfig", "hci0", "piscan"])
        subprocess.Popen(["sudo", "systemctl", "force-reload", "udev",
                          "systemd-udevd-control.socket", "systemd-udevd-kernel.socket"])


