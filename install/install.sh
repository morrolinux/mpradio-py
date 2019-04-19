if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

ln -s src/mpradio.py /home/pi/mpradio.py

apt-get -y install git libsndfile1-dev libbluetooth-dev bluez pi-bluetooth python-gobject python-gobject-2 bluez-tools sox ffmpeg libsox-fmt-mp3 python-dbus bluealsa obexpushd python3-rpi.gpio python3-mutagen python3-dbus python3-pip

# needed for rfcomm bluetooth interface
pip3 install pybluez


# install requirements as a dir. structure
for f in $(ls -d */)
do 
	sudo cp -R --parents $f /
done

# give execution permissions
for f in $(ls usr/local/bin)
do
	sudo chmod +x /usr/local/bin/$(basename $f)
done

# enable systemd units
for f in $(ls etc/systemd/system/*.service)
do 
	sudo systemctl enable $(basename $f)
done

systemctl enable bluetooth.service

cd /usr/local/src/
git clone https://github.com/Miegl/PiFmAdv.git
cd PiFmAdv/src
make clean
make -j $(nproc)

cp /usr/local/src/PiFmAdv/src/pi_fm_adv /usr/local/bin/pi_fm_adv

# set gpu_freq needed by PiFmAdv
if [[ $(grep "gpu_freq=250" /boot/config.txt) == "" ]]; then 	
    echo "gpu_freq=250" >> /boot/config.txt	
fi

# Final configuration and perms...
FSTAB="/etc/fstab"
fstabline=$(grep "pirateradio" $FSTAB -n|cut -d: -f1)
if [[ $fstabline == "" ]]; then
	echo "/dev/sda1    /pirateradio    vfat    defaults,rw,uid=pi,gid=pi,nofail 0   0" >> $FSTAB
fi

# usermod -a -G lp pi

usermod -aG bluetooth pi
chown -R pi:pi /pirateradio/
chmod +x /usr/lib/udev/bluetooth

# add dbus rule for user pi
bluez_pi=$(grep "policy user=\"pi\"" /etc/dbus-1/system.d/bluetooth.conf)
if [[ $bluez_pi == "" ]]; then
	sed -i '/<busconfig>/r bluez.txt' /etc/dbus-1/system.d/bluetooth.conf
fi

# set hostname
echo PRETTY_HOSTNAME=mpradio > /etc/machine-info
# avoid recompilation (by need2recompile.service) after first install 
cp -f /sys/firmware/devicetree/base/model /etc/lastmodel

sleep 5 && reboot
