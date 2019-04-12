sudo apt-get -y install git libsndfile1-dev libbluetooth-dev bluez pi-bluetooth python-gobject python-gobject-2 bluez-tools sox ffmpeg libsox-fmt-mp3 python-dbus bluealsa obexpushd python3-rpi.gpio 


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

