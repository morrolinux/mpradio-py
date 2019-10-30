#!/bin/bash

getSize(){ 
	size=$(sudo du -s --block-size M ${1} |cut -dM -f1)
	size=$(($size + 5))
	echo ${size}m
}

# SIZE=150m

# mount /tmp in tmpfs
mount -t tmpfs -o size=$(getSize /tmp) tmpfs /tmp

# mount /home/pi in tmpfs after copying its content
cd /
mkdir /tmp/home
cp -Rfp /home/pi/.* /tmp/home/
cp -Rfp /home/pi/mpradio* /tmp/home/
mount -t tmpfs -o size=$(getSize /home/pi/mpradio) tmpfs /home/pi
cp -Rfp /tmp/home/.* /home/pi/
cp -Rfp /tmp/home/mpradio* /home/pi/
cd /home/pi

# mount /etc in tmpfs
cd /
mkdir /tmp/etc
cp -Rfp /etc/* /tmp/etc/
mount -t tmpfs -o size=$(getSize /etc) tmpfs /etc
cp -Rfp /tmp/etc/* /etc/
cd /home/pi

# mount /pirateradio in tmpfs if no external rw filesystem is mounted
if [[ $(mount|grep pirateradio) == "" ]]
then
	cp -Rfp /pirateradio /tmp/
	mount -t tmpfs -o size=$SIZE tmpfs /pirateradio
	cp -Rfp /tmp/pirateradio/* /pirateradio/
fi
