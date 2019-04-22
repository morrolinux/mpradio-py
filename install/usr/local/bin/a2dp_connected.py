#!/usr/bin/env python3

# Note: this is not mine but I don't remember where does it come from.

from __future__ import absolute_import, print_function, unicode_literals

import dbus

bus = dbus.SystemBus()

manager = dbus.Interface(bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")


def extract_objects(object_list):
    list = ""
    for object in object_list:
        val = str(object)
        list = list + val[val.rfind("/") + 1:] + " "
    return list


def extract_uuids(uuid_list):
    list = ""
    for uuid in uuid_list:
        if (uuid.endswith("-0000-1000-8000-00805f9b34fb")):
            if (uuid.startswith("0000")):
                val = "0x" + uuid[4:8]
            else:
                val = "0x" + uuid[0:8]
        else:
            val = str(uuid)
        list = list + val + " "
    return list


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
                    print(properties["Address"])
