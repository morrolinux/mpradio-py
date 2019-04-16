#!/bin/bash

# bring up bluetooth interface
hciconfig hci0 up
hciconfig hci0 piscan

# make sure udev events are not being ignored
systemctl force-reload udev systemd-udevd-control.socket systemd-udevd-kernel.socket

# register bluetooth serial port
sdptool add SP
chgrp bluetooth /var/run/sdp
