# ARC Audio Routing — Discovery Brief

## Problem

The Pi 3B+ currently outputs audio to the Yamaha A-S301 via a USB-to-coaxial S/PDIF adapter. Two software sources already share this path: shairport-sync (AirPlay) and spotifyd. TV audio currently reaches the Yamaha via a separate TOSLINK cable. The goal is to bring TV audio into the Pi so that all audio sources route through a single coaxial input to the Yamaha, eliminating the TOSLINK cable.

ARC receive on the Pi 3B+ via the onboard HDMI port is not viable — the VC4 Linux driver implements HDMI audio output only. An external ARC receiver IC is required to get TV audio into the Pi.

## Intended Outcomes

- TV audio received by the Pi via an external ARC receiver IC and presented as a capture device
- All three audio sources (TV/ARC, shairport-sync, spotifyd) routed through the Pi to the USB coaxial S/PDIF adapter
- Yamaha A-S301 receives all audio on a single coaxial input
- TOSLINK cable eliminated

## Source Switching Model

Last-in wins. When a new audio source becomes active, the currently playing source is paused. No mixing. One source active at a time.

## Constraints

- Pi 3B+ is the routing host; no additional compute hardware
- DietPi OS
- Output device is the existing USB-to-coaxial S/PDIF adapter
- Yamaha A-S301 coaxial input accepts PCM stereo only — no compressed bitstream passthrough
- TV must be configured to output PCM over ARC
- ARC receiver IC required; connects between TV HDMI ARC port and Pi
- shairport-sync and spotifyd are the existing software streamers; audio routing stack must be compatible with both

## Assumptions

- An ARC receiver IC (e.g. CH482 or similar) can present TV audio to the Pi as a standard ALSA capture device
- Only one audio source is active at a time
- Sony Bravia can be configured to output PCM stereo over ARC
- DietPi can run PipeWire or PulseAudio capable of routing between multiple sources and one output

## Risks

- **ARC IC integration**: CH482 or similar may require custom driver work to appear as a capture device. Needs validation before design.
- **Audio routing stack**: shairport-sync and spotifyd have specific ALSA/PipeWire requirements. Multi-source sharing may require non-trivial configuration.
- **Source detection**: pausing an active source when a new one starts requires detecting source activity. May not be straightforward for all source types.
- **Latency**: Linux audio stack latency may affect TV audio lip sync.

## Open Questions

- Which ARC receiver IC is the right choice and does it present as a standard Linux audio capture device without custom driver work?
- Does last-in-wins require active source monitoring, or can it be achieved through PipeWire/PulseAudio routing policy alone?

