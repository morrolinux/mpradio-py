#!/bin/bash

getSize(){ 
	size=$(sudo du -s --block-size M ${1} |cut -dM -f1)
	size=$(($size + 5))
	echo ${size}
}

# SIZE=150m

# calculate tmpfs sizes
mpradioSize=$(getSize /home/pi/mpradio)
etcSize=$(getSize /etc)
pirateradioSize=0
if [[ $(mount|grep pirateradio) == "" ]]
then
	pirateradioSize=$(getSize /pirateradio)
fi
tmpSize=$(($mpradioSize + $etcSize + $pirateradioSize + $(getSize /tmp)))

# mount /tmp in tmpfs
mount -t tmpfs -o size=${tmpSize}m tmpfs /tmp

# mount /home/pi in tmpfs after copying its content
cd /
mkdir /tmp/home
cp -Rfp /home/pi/.* /tmp/home/
cp -Rfp /home/pi/mpradio* /tmp/home/
mount -t tmpfs -o size=${mpradioSize}m tmpfs /home/pi
mv /tmp/home/.* /home/pi/
mv /tmp/home/mpradio* /home/pi/
cd /home/pi

# mount /etc in tmpfs after copying its content
cd /
mkdir /tmp/etc
cp -Rfp /etc/* /tmp/etc/
mount -t tmpfs -o size=${etcSize}m tmpfs /etc
mv /tmp/etc/* /etc/
cd /home/pi

# mount /pirateradio in tmpfs if no external rw filesystem is mounted
if [[ $(mount|grep pirateradio) == "" ]]
then
	cp -Rfp /pirateradio /tmp/
	mount -t tmpfs -o size=${pirateradioSize}m tmpfs /pirateradio
	mv /tmp/pirateradio/* /pirateradio/
fi

