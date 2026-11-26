# Validation record

## Update v0.1.1 — 2026-11-26

- Fixed `HDD:\PERFORMER-AV.ini` loading (`hdd1:\` failed under DashLaunch autostart
  while `HDD:\` opens cleanly) and removed the hardcoded `192.168.1.13` fallback IP
  in stream21 (`SHA256`: `3c3f1da90c0a8a2951ff79151f249cf441492cbf3e51168154ca5d0066296b2e`).
- Confirmed after cold reboot (`magicboot cold` over XBDM) on the development
  console (`192.168.1.13`) with `PC_IP=192.168.1.4`: Xbox connected automatically to
  `192.168.1.4:36000` (`PC-Audio-Receiver.py`) and streamed real-time PCM
  (`callbacks: 2068 -> 2258`, `pumped: 2068 -> 2255` over 1 s, `dropped=0`, `errors=0`),
  with user confirmation of working audio.
- Confirmed the uncompressed image differs from stream20 only in the `HDD:\` INI path
  string and miss return (`26` bytes); capture, conversion, thread affinity, and
  streaming code are bit-for-bit unchanged.

## Confirmed on the development console — 2026-11-01

- User confirmed audio works with DashLaunch autostart in stream20, including Guide.
- Previous manual-loading tests confirmed game and dashboard capture.
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
existing LAN. Prolonged retry loops before starting the PC receiver (observed
after ~7 minutes without a listener) wedged `bounded_connect` inside `NetDll_select`;
starting **Start audio** before booting the Xbox avoids this. No measured
end-to-end latency, multichannel downmix validation, or repeated hardware
PC-restart acceptance run is claimed.
