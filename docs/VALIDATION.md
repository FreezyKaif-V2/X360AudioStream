# Validation record — 2026-11-01

## Confirmed on the development console

- User confirmed audio works with DashLaunch autostart in stream20, including Guide.
- Previous manual-loading tests confirmed game and dashboard capture.
- The release binary matches the exact user-accepted stream20 SHA256.
- Save to Xbox was exercised using the existing receiver address; upload and
  exact read-back passed. The destination was left unchanged.
- The Xbox install uses Xbox360Audio.xex, retains Aurora as default, and no
  longer autostarts xbGuard.

## Automated PC tests

Settings tests cover multiple IPv4 network prefixes, whitespace, invalid and
unsuitable destinations, duplicate keys, BOM/comment handling, preservation of
other settings, backup, upload and read-back against a mock XBDM server.
Volume tests cover command handling. The receiver test checks replacement of an
idle old connection by a waiting new connection. A hidden-process pipe test on
Windows confirmed stdin/stdout still work with CREATE_NO_WINDOW.

## Not established

This is not certification for every Xbox, router, subnet or sound device.
Other IP ranges were tested in software; the physical Xbox was tested on its
existing LAN. No measured end-to-end latency, multichannel downmix validation,
or repeated hardware PC-restart acceptance run is claimed.
