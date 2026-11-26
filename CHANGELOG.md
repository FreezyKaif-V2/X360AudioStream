# Changelog

## v0.1.1 — 2026-11-26

- Fixed `HDD:\PERFORMER-AV.ini` lookup under DashLaunch autostart (`hdd1:\` -> `HDD:\`) so receiver IP changes in `PC_IP` apply at boot.
- Removed the hardcoded `192.168.1.13` fallback IP when `PERFORMER-AV.ini` is missing; the plugin now retries reading configuration instead of connecting to a stale address.
- Kept audio capture, PCM conversion, thread affinity, and network streaming behavior unchanged from `v0.1.0`.
- Updated release docs and hardware validation notes.

## Initial documented build — 2026-11-01

- Standardized the accepted stream20 binary as Xbox360Audio.xex.
- System audio capture for Guide, original dashboard and games.
- Sender and conversion worker placement corrected for tested autostart behavior.
- Windowless Windows launcher, embedded logs and live volume acknowledgement.
- Default PC gain 200%.
- Full IPv4 receiver settings; backup and verified Save to Xbox through XBDM.
- Clean release layout, setup instructions and explicit validation limits.
