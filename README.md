# nc-pi-vision
Vision Processing on the Raspberry Pi for NC Robot


# Installation Notes for the Pi
## To start the python vision code on Pi startup
- Call the vision script from the `runCamera` script supplied in the FRC image in `/home/pi`
- E.g., add this line before the end of the script to invoke the python script and pass in any arguments to it that are required:
```
/home/pi/vision_main.py -oport next &
```
The ampersand at the end puts the process in the background and allows the next command in the script to run after it.

## To mount a USB drive on startup (which can be used for logging data and images)
- See Raspbian website for [detailed instructions](https://www.raspberrypi.org/documentation/configuration/external-storage.md)
- Mount the drive to `/mnt/usbdrv` using `sudo mkdir /mnt/usbdrv`
- Add this line to `/etc/fstab`
```
UUID=8832-D06B /mnt/usbdrv vfat defaults,auto,users,rw,nofail,x-systemd.device-timeout=15 0 0
```
- The UUID is obtained from this command `sudo blkid`. 
- Create symbolic link to `/mnt/usbdrv` in `/home/pi`:
```
/home/pi>ln -s /mnt/usbdrv
```
This will allow the vision code to log images and data to the usb drive at `/home/pi/usbdrv`
- Add alias to `~/.bash_aliases` file for unmounting the drive.  I.e.,
```
alias eject='sudo umount /mnt/usbdrv'
```
This will allow us to use `eject` command if we want to unmount the usb drive without shutting down the pi.  It should not be removed unless the pi is off or it has been unmounted.