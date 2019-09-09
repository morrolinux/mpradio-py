# mpradio-py
Morrolinux's Pirate radio (PiFmRDS implementation with Bluetooth and mp3 support) for all Raspberry Pi models

Work in progress.

The old implementation deeply relies on external services and it's not very object oriented nor flexible to changes, resulting in it being inconsistent in the user expirience across multiple devices and configurations. This project aims for a total rewrite with some structural changes to make it more modular, and try to integrate dependencies as much as possible for a better management.

# Features
Exclusively tested on Minimal Raspbian (ARM)
- [x] Resume track from its playback status hh:mm:ss across reboots (CD-like expirience)
- [x] Shuffle on/off
- [x] Display track info over RDS (for both bluetooth playback and music on local storage)
- [x] Skip song by pressing a push-button (GPIO-connected on pin 5 [BCM 3]) even when playing bluetooth audio
- [x] Safely power on/off by holding the push-button
- [x] Stream audio over FM or 3.5mm Jack (As a Bluetooth speaker via jack audio output)
- [ ] Send mp3 files or zip/rar albums to the Pi via Bluetooth
- [ ] Bluetooth OTA file management on the Pi with applications such as "Bluetooth Explorer Lite"
- [x] Read metadata from mp3 files
- [x] Play local music in multiple formats [ogg/m4a/mp3/wav/flac]
- [ ] Read Only mode for saving sdcard from corruption when unplugging AC
- [x] PiFmAdv (default)(experimental) implementation for better signal purity 
- [x] Multiple remotes available (GPIO pushbutton / Bluetooth Android App / Control Pipe via shell)
- [ ] Update just mpradio by sending mpradio-master.zip via Bluetooth (Update via App will be soon available)
- [ ] Bluetooth companion app for android (Work in progress...) 

# Installation
`git clone https://github.com/morrolinux/mpradio-py.git mpradio`

`cd mpradio/install && sudo bash install.sh`

# Configuration
By default, `mpradio` will always be running automatically after boot once installed. No additional configuration is needed.
However, you can change the FM streaming frequency (which is otherwise defaulted to 88.0) by placing a file named pirateradio.config in the root of a USB key (which of course, will need to stay plugged for the settings to be permanent)

default `pirateradio.config` here: https://github.com/morrolinux/mpradio-py/blob/master/install/pirateradio/pirateradio.config

### Optional: Protect your SD card from corruption by setting Read-Only mode.

use utility/roswitch.sh as follows:

`sudo bash roswitch.sh ro` to enable read-ony (effective from next boot)

`sudo bash roswitch.sh rw` to disable read-only (effective immediately)


# Known issues
- Due to a design flaw in BCM43438 WIFI/BT chipset, you might need to disable WiFi if you experience BT audio stuttering on Pi Zero W and Pi 3: https://github.com/raspberrypi/linux/issues/1402 - you can switch onbloard WiFi on/off using `wifi-switch` command (even via Bluetooth link on the Android companion app typing in "settings" > "command" section) 
- Boot can take as long as 1m30s on the Pi 1 and 2 due to BT UART interface missing on the board.
  Reducing systemd timeout with `echo "DefaultTimeoutStartSec=40s" >> /etc/systemd/system.conf` should help

# Usage
It (should) work out of the box. You need your mp3 files to be on a FAT32 USB stick (along with the `pirateradio.config` file if you want to override the default settings).
You can **safely** shut down the Pi by holding the push button or via App, and waiting for about 5 seconds until the status LED stops blinking.
If you add new songs on the USB stick, they won't be played until the current playlist is consumed. You can "rebuild" the playlist (looking for new recently added files) if needed:
- Via App 

or

- Simply delete `playlist.json` and `library.json` from your USB stick when you add new songs to it.
  
Also, please remember that (though it would be probably illegal) you can test FM broadcasting by plugging a 20cm wire on the **GPIO 4** of your Pi.

## Control pipe
You can perform certain operations while `mpradio.service` is running by simply writing to `/tmp/mpradio_bt`

Example:
* Playback control:  `echo "previous|next|resume|pause" > mpradio_bt`
* System commands: `echo "poweroff|reboot" > mpradio_bt`

## Bluetooth companion app 

I'll post the source code once it's mature enough, but you can test an alpha (0.2) version [here](http://www.mediafire.com/file/awu3r50z5gz3363/mpradio_remote-0.2.apk) 

NB: I haven't handled all corner conditions yet, so crashes may occour. (Make sure your Bluetooth is on and your Pi is paired, before even starting the app) 

# Contributing
## Guidelines
One important requirement is for the program to be mostly testable on your developement machine instead of having to be copied to a Pi each time for testing. This speeds things up, from developing to testing and debugging. To acheive this, I've put platform checks within the code which should be run differently on a Pi rather than on a PC. If you happen to create logic which is supposed to be tested only on a Pi, please insert a platform check not to produce any execution errors on a PC.

## Path
If you're testing on your computer, please `cd` to the `mpradio/src` folder and run `./mpradio.py`

# Debugging / Troubleshooting
## Services
`mpradio` is launched as a service (via systemd) upon each boot.

To check whether the service is running or not: 

` $ sudo systemctl status mpradio `

To start or stop the service:

` $ sudo systemctl [start/stop] mpradio `

## Bluetooth

Bluetooth connection logs are found at ` /var/log/bluetooth_dev `.

If the Raspberry Pi is not showing up as a Bluetooth device, check whether the interface is UP, and that the `bt-setup` script is running:

` $ hciconfig `

` $ sudo systemctl status bt-setup `

If you are having issues with pairing Bluetooth for audio, please also check if `simple-agent` service is running:

` $ sudo systemctl status simple-agent `

If you are having issues with Bluetooth not connecting once it's paired, please check whether `bluealsa` is running or not:

` $ sudo systemctl status bluealsa `

A simple schematic of how things work together:

![MPRadio schematic](/doc/mpradio_schematic.png?raw=true "mpradio schematic")

# Warning and Disclaimer
`mpradio` relies on PiFmAdv for FM-Streaming feature. Please note that in most states, transmitting radio waves without a state-issued licence specific to the transmission modalities (frequency, power, bandwidth, etc.) is illegal. Always use a shield between your radio receiver and the Raspberry. Never use an antenna. See PiFmAdv Waring and Disclamer for more information.
