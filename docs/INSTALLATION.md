# Installation and networking

Use the Xbox dashboard network settings to find the Xbox IPv4 address. On
Windows, run `ipconfig` and find the IPv4 address of the adapter connected to
the same network. Do not use a VPN or virtual-adapter address unless you have
explicitly configured routing between the devices. A DHCP reservation helps
keep the PC address stable.

The PC settings window accepts full IPv4 addresses. Examples include
`192.168.0.50`, `10.0.0.50` and `172.16.8.12`. There is no fixed subnet prefix.
IPv6, hostnames, loopback, unspecified, multicast and the limited broadcast
address are not accepted as receiver destinations. A subnet-directed broadcast
cannot be recognized without the network mask; enter an actual host address.

Different subnets require working routing. Windows Firewall must permit inbound
TCP 36000 for the receiver on the trusted LAN. Save to Xbox independently needs
access from the PC to the Xbox's XBDM port 730; it does not use FTP credentials.
Do not expose the receiver or debug connection to the public Internet.

Settings are stored in `HDD:\PERFORMER-AV.ini`. The legacy filename is intentional
because the Xbox binary reads it. Only PC_IP is changed; other entries are kept.
Duplicate PC_IP entries are collapsed to one. Existing file bytes are backed up
under `pc/config-backups/` before writing. The generated file must fit the XEX's
1023-byte parser limit. A failed verification is an error, not a successful save;
restore the backup if an interrupted transfer leaves the file damaged.

Reboot after changing PC_IP. Do not unload a resident capture plugin in a menu;
use a reboot to stop or replace it. xbGuard is not required for normal autostart.
Keep your existing Aurora/default-launcher configuration and unrelated plugins.

For an upgrade, stop playback, back up the existing XEX and launch.ini, replace
the XEX, then reboot. Keep only one audio plugin entry. Verify the provided SHA256
with `Get-FileHash xbox/Xbox360Audio.xex -Algorithm SHA256` before installation.
