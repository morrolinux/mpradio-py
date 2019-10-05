#!/bin/bash

SIZE=150m

# mount /tmp in tmpfs
mount -t tmpfs -o size=$SIZE tmpfs /tmp

# mount /home/pi in tmpfs after copying its content
cd /
mkdir /tmp/home
cp -Rfp /home/pi/.* /tmp/home/
cp -Rfp /home/pi/mpradio* /tmp/home/

mount -t tmpfs -o size=$SIZE tmpfs /home/pi

cp -Rfp /tmp/home/.* /home/pi/
cp -Rfp /tmp/home/mpradio* /home/pi/
cd /home/pi

# mount /pirateradio in tmpfs if no external rw filesystem is mounted
if [[ $(mount|grep pirateradio) == "" ]]
then
	cp -Rfp /pirateradio /tmp/
	mount -t tmpfs -o size=$SIZE tmpfs /pirateradio
	cp -Rfp /tmp/pirateradio/* /pirateradio/
fi
