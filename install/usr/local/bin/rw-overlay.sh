#!/bin/bash

SIZE=150m

mount -t tmpfs -o size=$SIZE tmpfs /tmp

cd /
mkdir /tmp/home
cp -Rfp /home/pi/.* /tmp/home/
cp -Rfp /home/pi/mpradio* /tmp/home/

mount -t tmpfs -o size=$SIZE tmpfs /home/pi

cp -Rfp /tmp/home/.* /home/pi/
cp -Rfp /tmp/home/mpradio* /home/pi/

cd /home/pi
