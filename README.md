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
