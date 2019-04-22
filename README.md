# mpradio-py
Morrolinux's Pirate radio (PiFmRDS implementation with Bluetooth and mp3 support) for all Raspberry Pi models

Work in progress.

The old implementation deeply relies on external services and it's not very object oriented nor flexible to changes, resulting in it being inconsistent in the user expirience across multiple devices and configurations. This project aims for a total rewrite with some structural changes to make it more modular, and try to integrate dependencies as much as possible for a better management.

# Contributing
## Guidelines
One important requirement is for the program to be mostly testable on your developement machine instead of having to be copied to a Pi each time for testing. This speeds things up, from developing to testing and debugging. To acheive this, I've put platform checks within the code which should be run differently on a Pi rather than on a PC. If you happen to create logic which is supposed to be tested only on a Pi, please insert a platform check not to produce any execution errors on a PC.

## Path
If you're testing on your computer, please `cd` to the `mpradio/src` folder and run `./mpradio.py`


# Features
Exclusively tested on Minimal Raspbian (ARM)
- [x] Resume track from its playback status hh:mm:ss across reboots (CD-like expirience)
- [x] Shuffle on/off
- [x] Customizable scrolling RDS to overcome 8-chars limitation
- [x] Skip to the next song by pressing a push-button (GPIO-connected on pin 18)
- [x] Safely shutdown by holding the push-button (GPIO-connected on pin 18)
- [x] Stream audio over FM or 3.5mm Jack (Bluetooth speaker via jack audio output)
- [ ] Send mp3 files or zip/rar albums to the Pi via Bluetooth
- [ ] Bluetooth OTA file management on the Pi with applications such as "Bluetooth Explorer Lite"
- [x] Read metadata from the mp3 files 
- [x] Multiple file format support [mp3/wav/flac]
- [ ] Read Only mode for saving sdcard from corruption when unplugging AC
- [x] PiFmAdv (default)(experimental) implementation for better signal purity 
- [x] Control pipe commands during playback (explained below)
- [ ] Update just mpradio by sending mpradio-master.zip via Bluetooth (Update via App will be soon available)
- [ ] Bluetooth companion app for android (Work in progress...) 
- [ ] Display Android notifications over RDS?
- [ ] Automatically partition the sdcard for a dedicated mp3 storage space (instead of using a USB drive)

# Installation
`git clone https://github.com/morrolinux/mpradio-py.git mpradio`
`cd mpradio/install && sudo bash install.sh`
