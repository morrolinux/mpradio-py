#!/bin/bash

currentmodel="/sys/firmware/devicetree/base/model"
lastmodel="/etc/lastmodel"

diff $currentmodel $lastmodel
equals=$?

if [[ $equals -eq 1 ]]
then
	mount -o remount rw /

	cp $currentmodel $lastmodel
	systemctl stop mpradio
	
	cd /usr/local/src/PiFmAdv/src/
	make clean
	make

	cp /usr/local/src/PiFmAdv/src/pi_fm_adv /usr/local/bin/pi_fm_adv
	
	reboot
fi
