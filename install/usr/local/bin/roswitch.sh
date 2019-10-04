#!/bin/bash

if [ "$#" -ne 1 ]; then
        echo "Illegal number of parameters"
        exit
fi

if [[ $1 == "ro" ]]
then
        sed -i.bak '/^PARTUUID/ s/defaults/defaults,ro/' /etc/fstab
        sed -i.bak 's/rootwait *$/rootwait noswap ro/' /boot/cmdline.txt

        if [[ $(sudo grep "var" /etc/fstab) == "" ]]
        then
                echo "tmpfs /var tmpfs noatime 0 0" >> /etc/fstab
        fi

        echo "You need to reboot to make this effective."
elif [[ $1 == "rw" ]]
then
	cd /
	umount /home/pi		# umount overlay tmpfs rw filesystem if present
        mount -o remount,rw /
        mount -o remount,rw /boot
        sed -i.bak '/^PARTUUID/ s/defaults,ro/defaults/' /etc/fstab
        sed -i.bak 's/rootwait noswap ro*$/rootwait/' /boot/cmdline.txt
        umount -l /var/
	sed -i '/tmpfs \/var tmpfs noatime 0 0/d' /etc/fstab
        echo "RW effective now!"
	cd -
fi
