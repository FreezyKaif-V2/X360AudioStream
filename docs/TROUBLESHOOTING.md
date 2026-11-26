# Troubleshooting

## No connection

Click **Start audio** before booting the Xbox; opening the window alone does
not start the receiver. Check `PC_IP` in `HDD:\PERFORMER-AV.ini`, the active PC
adapter, TCP 36000 firewall access, and the DashLaunch plugin path. Reboot
after editing Xbox settings. Only one receiver can listen on port 36000. A
connection may take a few seconds after the receiver starts.

If the Xbox was booted while the receiver was closed and retried for several
minutes without connecting after **Start audio** was clicked, reboot the Xbox
while **Start audio** is running.

## Save to Xbox fails

Check the Xbox address and whether XBDM is installed and reachable on TCP 730.
FTP being available does not establish XBDM availability. For manual setup,
edit PERFORMER-AV.ini and transfer it using your normal file-transfer tool.
Use a full IPv4 address, not a hostname. The success dialog appears only after
the uploaded file is read back and matches the requested bytes.

## Connected but quiet

Aurora normally has no navigation audio. Test Guide navigation, the original
dashboard or a game. Check the selected PC output device and the volume slider.
An **Applied** message acknowledges the volume command, not successful playback.
An audio driver error requires fixing/selecting an available output device and
restarting audio. A -96 dB reading can simply mean silence.

## Delay or distortion

Try wired audio rather than Bluetooth. The printed device latency excludes
capture, network and other playback buffers. Reduce volume if 200% clips.
Avoid multiple audio plugin copies. Do not replace this build with old test XEXs.

## Command-line use

`python pc/PC-Audio-Receiver.py --list-devices`

`python pc/PC-Audio-Receiver.py --device DEVICE_ID --volume 200`

The default requests the device's low-latency setting. `--latency-ms` requests
a device latency; it does not guarantee the end-to-end delay.
