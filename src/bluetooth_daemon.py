import subprocess


class BluetoothDaemon:

    simpleagent = None
    bluealsa = None

    def __init__(self):
        self.bt_setup()
        self.run_bluealsa()
        self.run_simple_agent()

    def run_simple_agent(self):
        subprocess.Popen(["sudo", "killall", "simple-agent"]).wait(5)
        self.simpleagent = subprocess.Popen(["sudo", "simple-agent"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def run_bluealsa(self):
        subprocess.Popen(["sudo", "killall", "bluealsa"]).wait(5)
        self.bluealsa = subprocess.Popen(["sudo", "bluealsa", "-p", "a2dp-sink", "--a2dp-force-audio-cd"],
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def bt_setup(self):
        subprocess.Popen(["sudo", "hciconfig", "hci0", "up"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.Popen(["sudo", "hciconfig", "hci0", "piscan"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.Popen(["sudo", "systemctl", "force-reload", "udev", "systemd-udevd-control.socket",
                          "systemd-udevd-kernel.socket"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def restart_simple_agent(self):
        self.simpleagent.kill()
        self.run_simple_agent()

    def restart_bluealsa(self):
        self.bluealsa.kill()
        self.run_bluealsa()
