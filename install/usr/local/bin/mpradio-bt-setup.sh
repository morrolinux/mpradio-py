#!/bin/bash

# bring up bluetooth interface
hciconfig hci0 up
hciconfig hci0 piscan

# make sure udev events are not being ignored
systemctl force-reload udev systemd-udevd-control.socket systemd-udevd-kernel.socket

# start needed services
simple-agent &
bluealsa -p a2dp-sink --a2dp-force-audio-cd &
