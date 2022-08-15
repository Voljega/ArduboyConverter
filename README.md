[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/donate?hosted_button_id=LEAH843NKNG72)

# ArduboyConverter

A custom converter of Eried's Arduboy Collection to EmulationStation based distributions

## Arduboy Collection

The collection is located [here](https://github.com/eried/ArduboyCollection)

The tool will automatically download the collection the first time

## The Tool

Usage is pretty simple:
- Enter your output dir, be warned its content will be erased when proceeding with the conversion
- `Auto Update` allows the tool to get the latest modification of the collection when checked
- `Use genre subfolders` will create subfolders for genre if checked

### Linux/MacOS installation and execution :
- ArduboyConverter requires that python3 is installed (it's developed on 3.8)
- first install Tkinter for python3 if needed : `sudo apt-get install python3-tk`
- directly download sources or clone the repo with :
 ```
 sudo apt install git # optional, only if git is not installed
 git clone https://github.com/Voljega/ArduboyConverter
 ```
- give execution rights to `ArduboyConverter.sh` :
```
cd ArduboyConverter            # change to ArduboyConverter directory
chmod u+x ArduboyConverter.sh  # give execution perms (already done in git-cloned version)
```
- launch with `./ArduboyConverter.sh` or `./ArduboyConverter`

### Windows installation and execution :

Either use the latest [release](https://github.com/Voljega/ArduboyConverter/releases) or you can build your own version (see `build.txt`)

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate?hosted_button_id=LEAH843NKNG72)
