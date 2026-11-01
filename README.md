# X360AudioStream

Stream Xbox 360 audio to your Windows PC over your local network. Listen to games, dashboard audio and Xbox Guide sound effects through your PC's speakers or headphones.

## Features

- System audio streaming with DashLaunch autostart or temporary loading through xbGuard.
- Uncompressed 48 kHz, 16-bit stereo audio.
- Live PC volume control with a default level of 200%.
- Automatic connection retry when the receiver is unavailable.
- Windowless PC app with output-device selection and connection logs.
- Receiver IP settings that can be saved directly to the Xbox.

## Downloads

Get both files from the [v0.1.0 release](https://github.com/FreezyKaif-V2/X360AudioStream/releases/tag/v0.1.0):

| File | Purpose |
| --- | --- |
| [Xbox360Audio.xex](https://github.com/FreezyKaif-V2/X360AudioStream/releases/download/v0.1.0/Xbox360Audio.xex) | Xbox audio plugin |
| [X360AudioStream-PC-v0.1.0.zip](https://github.com/FreezyKaif-V2/X360AudioStream/releases/download/v0.1.0/X360AudioStream-PC-v0.1.0.zip) | Windows receiver app |

Download the attached PC ZIP rather than GitHub's automatic **Source code** archives. The PC app requires Python; it is not a standalone EXE.

## Requirements

- A modified Xbox 360 with DashLaunch for autostart, or xbGuard for temporary plugin loading.
- Windows with Python 3.10+ and Tkinter, with Python added to PATH.
- A network connection between the Xbox and PC.
- Inbound TCP port **36000** allowed for the PC receiver through Windows Firewall.
- XBDM on the Xbox, reachable on TCP **730**, to use **Save to Xbox**. You can also configure the receiver IP manually without XBDM.

## Setup

### 1. Install the Xbox plugin

Copy `Xbox360Audio.xex` to the root of the Xbox HDD.

**Option A — DashLaunch autostart**

In your existing `HDD:\launch.ini`, add the following path to a free slot under `[Plugins]`:

```ini
[Plugins]
plugin4 = HDD:\Xbox360Audio.xex
```

Use a different slot number if `plugin4` is occupied. Keep your existing launcher and other plugin entries. xbGuard is not required for this method.

**Option B — xbGuard temporary loading**

You can load the audio plugin through xbGuard without adding it to DashLaunch autostart. Finish the PC setup and receiver-address configuration below before loading it.

If the audio plugin is already configured in `launch.ini`, remove that audio entry and reboot before using temporary loading. **Do not load another copy through xbGuard while a copy is already running.**

### 2. Set up the PC app

Extract the PC ZIP. Open a terminal in the extracted folder containing `requirements.txt` and run:

```powershell
python -m pip install -r requirements.txt
```

Open `Start-Xbox-Audio.vbs` to launch the app without a console window.

### 3. Set the receiver address

In the PC app, open **Xbox connection settings**:

1. Enter the Xbox's IPv4 address.
2. Enter the PC's IPv4 address on the network connected to the Xbox.
3. Click **Save to Xbox**.

The app backs up existing settings and verifies the saved file. Full IPv4 addresses are supported, including networks such as `192.168.0.x`, `192.168.1.x` and `10.0.0.x`.

**Manual configuration:** create or edit `HDD:\PERFORMER-AV.ini` and set `PC_IP` to your PC's address:

```ini
PC_IP=192.168.1.100
```

Replace the example address with your own and preserve any other settings in the file. Keep the filename `PERFORMER-AV.ini` exactly as shown.

### 4. Start listening

Choose an output device in the PC app and click **Start audio**, then use your chosen loading method:

- **DashLaunch:** reboot the Xbox to load the plugin automatically and apply its settings.
- **xbGuard:** open xbGuard's temporary plugin-loading menu and select `HDD:\Xbox360Audio.xex`. Load it once; it remains active for the current console session. After rebooting, load it again through xbGuard.

To stop or replace a temporarily loaded audio plugin, reboot the Xbox. Do not use xbGuard's unload option while the audio plugin is running.

For later sessions, open the app and click **Start audio**. The plugin automatically retries the connection when the receiver becomes available.

## Using the app

- **Volume:** changes apply during playback. 0% mutes, 100% leaves the level unchanged, and the default 200% boosts quieter sounds. Lower the volume if loud audio distorts. This controls PC playback volume.
- **Output device:** choose the device before starting audio. Stop and restart audio after changing it.
- **Stop audio:** stops the PC receiver. Click **Start audio** to listen again.
- **Connection settings:** reboot the Xbox after changing the receiver IP. If using xbGuard temporary loading, load the plugin again after the reboot. A DHCP reservation can help keep the PC address stable.

## Troubleshooting

| Problem | What to check |
| --- | --- |
| No connection | Click **Start audio**, check the PC IP and firewall, and confirm the plugin is loaded through DashLaunch or xbGuard. |
| Save to Xbox fails | Check the Xbox IP and XBDM access on TCP 730. FTP access alone is not sufficient. |
| Connected but silent | Check the output device and volume. Test a game or Guide navigation; Aurora normally has no navigation sounds. |
| Audio driver error | Select an available output device and restart audio. |
| Delayed or distorted sound | Try wired headphones or speakers, and reduce volume if the audio clips. |

Keep only one PC receiver running on port 36000. To replace or stop the resident Xbox plugin, reboot the console rather than unloading it while it is running.

## Audio format

| Setting | Value |
| --- | --- |
| Sample rate | 48 kHz |
| Channels | Stereo |
| Sample format | Signed 16-bit PCM |
| Audio bitrate | Approximately 1.536 Mbps, excluding network headers |
| Transport | TCP |

Playback delay depends on the network and output device. The latency shown in the app is the audio device's reported latency, not the total Xbox-to-speaker delay.

## Documentation and credits

- [Installation and networking](docs/INSTALLATION.md)
- [Troubleshooting and command-line options](docs/TROUBLESHOOTING.md)
- [Developer documentation](docs/DEVELOPMENT.md)
- [Credits and component provenance](THIRD_PARTY_NOTICES.md)

Original 360Stream base by [u/SirDankz](https://www.reddit.com/user/SirDankz/).
