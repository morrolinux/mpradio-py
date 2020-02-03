from __future__ import absolute_import, print_function, unicode_literals
import dbus
import subprocess


class BluetoothDaemon:

    __simpleagent = None
    __bluealsa = None

    def __init__(self):
        self.bt_setup()
        self.run_bluealsa()
        self.run_simple_agent()

    def run_simple_agent(self):
        subprocess.Popen(["sudo", "killall", "simple-agent"]).wait(5)
        self.__simpleagent = subprocess.Popen(["sudo", "simple-agent"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def run_bluealsa(self):
        subprocess.Popen(["sudo", "killall", "bluealsa"]).wait(5)
        self.__bluealsa = subprocess.Popen(["sudo", "bluealsa", "-p", "a2dp-sink", "--a2dp-force-audio-cd"],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def bt_setup(self):
        subprocess.Popen(["sudo", "hciconfig", "hci0", "up"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.Popen(["sudo", "hciconfig", "hci0", "piscan"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.Popen(["sudo", "systemctl", "force-reload", "udev", "systemd-udevd-control.socket",
                          "systemd-udevd-kernel.socket"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    @staticmethod
    def get_connected_device():
        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")
        objects = manager.GetManagedObjects()

        all_devices = (str(path) for path, interfaces in objects.items() if
                       "org.bluez.Device1" in interfaces.keys())

        for path, interfaces in objects.items():
            if "org.bluez.Adapter1" not in interfaces.keys():
                continue

            device_list = [d for d in all_devices if d.startswith(path + "/")]

            for dev_path in device_list:

                dev = objects[dev_path]
                properties = dev["org.bluez.Device1"]

                for key in properties.keys():
                    value = properties[key]
                    if key == "Connected":
                        if value == 1:
                            return properties["Address"]

    def restart_simple_agent(self):
        self.__simpleagent.kill()
        self.run_simple_agent()

    def restart_bluealsa(self):
        self.__bluealsa.kill()
        self.run_bluealsa()
