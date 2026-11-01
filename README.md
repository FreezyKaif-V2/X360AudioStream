# X360AudioStream

Stream Xbox 360 system audio to a Windows PC over your local network.
The Xbox plugin starts through DashLaunch; the PC app plays the stream with
live volume control and a default volume of 200%.

The current Xbox build is the user-tested **stream20** build, distributed as
`Xbox360Audio.xex`. Guide sound effects, the original dashboard and game audio
have been confirmed on the development console. Aurora itself normally has
no navigation sounds. There is no custom Guide UI.

## Download

[Download Xbox360Audio.xex](https://github.com/FreezyKaif-V2/X360AudioStream/raw/refs/heads/main/xbox/Xbox360Audio.xex)

The binary matches the tested stream20 build. Verify it against [SHA256SUMS.txt](SHA256SUMS.txt).

## Requirements

- A modified Xbox 360 that can load DashLaunch plugins.
- A Windows PC with Python 3.10+ and Tkinter.
- Both devices reachable on the local network. The receiver listens on TCP 36000.
- XBDM on the Xbox (TCP 730) if using **Xbox connection settings → Save to Xbox**.
  Manual editing of the INI is also supported and does not require XBDM.

## Quick start

1. Install PC dependencies from this folder:
   `python -m pip install -r pc/requirements.txt`
2. Copy `xbox/Xbox360Audio.xex` to `HDD:\Xbox360Audio.xex`.
3. Copy `xbox/PERFORMER-AV.ini.example` to `HDD:\PERFORMER-AV.ini` and set
   `PC_IP` to your PC's actual IPv4 address. Preserve an existing config if present.
4. In your existing `HDD:\launch.ini`, set one free plugin slot to
   `HDD:\Xbox360Audio.xex`. See `xbox/launch.ini.example`; do not replace your
   entire launch.ini with that example.
5. Open `pc/Start-Xbox-Audio.vbs`, choose the output device and click **Start audio**.
6. Reboot the Xbox to load the plugin. Do not load a second copy manually.

The `.vbs` launcher opens only the app window. The `.bat` compatibility launcher
may briefly flash a command window. Logs appear inside the app.

To change the receiver address later, open **Xbox connection settings**, enter
the Xbox and PC full IPv4 addresses, and select **Save to Xbox**. The app backs
up existing settings and reads the saved file back to verify it. Reboot the
Xbox after changing the address. It is not restricted to `192.168.1.x`.

## Playback and reconnection

Volume changes apply while playing; **Applied …%** means the receiver accepted
the setting. 0% mutes and 100% is unity gain. The default 200% helps quieter
system sounds but can clip loud material. This is PC output gain, not Xbox TV volume.

The plugin retries if the PC receiver starts later or closes. Reopen the app
and click **Start audio** to listen again. Repeated restart behavior is supported
by the code but has not yet received repeated hardware acceptance testing.

Audio is uncompressed 48 kHz, stereo, signed 16-bit PCM, approximately 1.536 Mbps
before headers. There is no measured end-to-end latency guarantee. The output
latency printed by the app is only the audio device's reported latency.

## Documentation

- [Installation and networking](docs/INSTALLATION.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Architecture and build limitations](docs/DEVELOPMENT.md)
- [Validation record](docs/VALIDATION.md)
- [Credits and component provenance](THIRD_PARTY_NOTICES.md)

Original 360Stream base by [u/SirDankz](https://www.reddit.com/user/SirDankz/).
This repository contains the PC app, capture additions and the patched Xbox
binary; it is **not a complete from-source rebuild of the original XEX**.
