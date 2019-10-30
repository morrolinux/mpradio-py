#!/bin/bash

if [ "$#" -ne 1 ]
then
        echo "usage: sudo roswitch <rw|ro|status>"
        exit
fi

check_status () {
	RO=0
	declare -A tests
	
	tests['root_RO']=$(if [[ $(mount|grep "/dev/mmcblk0p2"|grep "ro") != "" ]]; then echo "1"; else echo "0"; fi)
	tests['tmp_tmpfs']=$(if [[ ${tests['root_RO']} -eq 1 ]] && 
		[[ $(mount|grep "/tmp"|grep "tmpfs") != "" ]]; then echo "1"; else echo "0"; fi)
	tests['home_tmpfs']=$(if [[ $(mount|grep "/home/pi"|grep "tmpfs") != "" ]]; then echo "1"; else echo "0"; fi)
	tests['home_content_copied']=$(if [[ ${tests['home_tmpfs']} -eq 1 ]] && 
		[[ $(ls /home/pi|grep "mpradio") != "" ]]; then echo "1"; else echo "0"; fi)
	tests['service_ran']=$(if [[ $(sudo systemctl status rw-overlay|grep "Process"|grep "SUCCESS") != "" ]]; 
		then echo "1"; else echo "0"; fi)
	tests['pirateradio_tmpfs']=$(if [[ ${tests['root_RO']} -eq 1 ]] && 
		[[ $(mount|grep pirateradio) != "" ]]; then echo "1"; else echo "0"; fi)
	tests['pirateradio_content_copied']=$(if [[ ${tests['pirateradio_tmpfs']} -eq 1 ]] && 
		[[ $(ls /pirateradio) != "" ]]; then echo "1"; else echo "0"; fi)
	tests['etc_tmpfs']=$(if [[ $(mount|grep "/etc"|grep "tmpfs") != "" ]]; then echo "1"; else echo "0"; fi)
	tests['etc_content_copied']=$(if [[ ${tests['etc_tmpfs']} -eq 1 ]] && 
		[[ $(ls /etc) != "" ]]; then echo "1"; else echo "0"; fi)

	for elem in ${!tests[@]}
	do 
		(( RO+=${tests[$elem]} ))
	done
	
	if [[ $RO -eq ${#tests[@]} ]]
	then
		echo "RO mode"
	elif [[ $RO -eq 0 ]]
	then
		echo "RW mode"
	else
		echo "inconsistent state! (${RO}/${#tests[@]})"
		for elem in ${!tests[@]}
		do 
			echo $elem : ${tests[$elem]}
		done
	fi
	
	pirateradio_mounted=$(if [[ $(mount|grep pirateradio) == "" ]]; then echo "not mounted"; else echo "mounted"; fi)

	echo "/pirateradio folder status: $pirateradio_mounted"
	
	unset tests
}


if [[ $1 == "ro" ]]
then
        sed -i.bak '/^PARTUUID/ s/defaults/defaults,ro/' /etc/fstab
        sed -i.bak 's/rootwait *$/rootwait noswap ro/' /boot/cmdline.txt

        if [[ $(sudo grep "var" /etc/fstab) == "" ]]
        then
                echo "tmpfs /var tmpfs noatime 0 0" >> /etc/fstab
        fi

	systemctl enable rw-overlay.service
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
	systemctl disable rw-overlay.service
        echo "RW effective now!"
	cd -
elif [[ $1 == "status" ]]
then
	check_status
fi
