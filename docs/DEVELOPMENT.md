# Architecture and build status

The resident plugin captures the mixed system render stream through kernel MEC
exports 800/802. A bounded 16-frame handoff keeps conversion and network I/O out
of the render callback. Each capture contains 256 samples in six planar float
channels; the converter selects the first two channels for stereo 16-bit PCM.
This is not a validated surround downmix.

The conversion worker writes a 64-slot PCM queue consumed by the original
streamer's network worker. Each worker uses hardware thread 3 in the accepted
stream20 binary. This placement fixed the observed autostart Guide failure on
the development console. Bounded connect attempts retain the reconnect loop.

The PC receiver accepts the original 28-byte big-endian HY37 packet header and
plays little-endian PCM through sounddevice. Its GUI controls the receiver through
stdin and receives logs/volume acknowledgements through stdout. Hidden child
processes retain those pipes.

## Source scope

`source/capture` contains the new capture, queue, conversion and connect logic
plus host tests. It calls fixed addresses in the original binary. It is not a
standalone plugin and cannot be linked at arbitrary addresses.

The shipped XEX is a patched original 360Stream binary. The original complete
source is not present, so this clean distribution does not promise a fully
reproducible from-source XEX build. The development workspace retains the original
containers, patch builders and experimental artifacts; those are intentionally
not part of the release folder. Microsoft SDKs and XEXTool are not bundled.

## Host tests

`python -m unittest discover -s pc -p "test_*.py"`

With a native C compiler, from source/capture:

`cc -std=c11 -Wall -Wextra -Werror mec_handoff.c test_handoff.c -o test_handoff`

`cc -std=c11 -Wall -Wextra -Werror pcm_convert.c test_pcm_convert.c -lm -o test_pcm_convert`

Run both resulting executables. Host tests do not establish Xbox UI, kernel or
autostart behavior. There is no custom Guide panel in this release.
