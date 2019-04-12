sudo apt-get -y install git libsndfile1-dev libbluetooth-dev bluez pi-bluetooth python-gobject python-gobject-2 bluez-tools sox ffmpeg libsox-fmt-mp3 python-dbus bluealsa obexpushd python3-rpi.gpio 


for f in $(ls -d */)
do 
	sudo cp -R --parents $f /
done

for f in $(ls etc/systemd/system/*.service)
do 
	sudo systemctl enable $(basename $f)
done

