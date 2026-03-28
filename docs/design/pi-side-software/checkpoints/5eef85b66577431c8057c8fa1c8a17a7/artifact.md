# Design Unit 1 — Pi-Side Software

## Status

**Ready.**

## Problem

Accept commands from two independent input sources (HDMI-CEC, BLE side-door device) and translate them to Yamaha A-S301 IR transmissions with no missed commands when the Pi is running.

## Solution Structure

Single Python process with four components and a shared asyncio event loop.

### 1. Command Map

Static mapping of logical command names to NEC scancodes. Single source of truth for both input paths.

| Command         | Scancode |
|-----------------|----------|
| `power`         | `0x7e2a` |
| `volume_up`     | `0x7a1a` |
| `volume_down`   | `0x7a1b` |
| `mute`          | `0x7a1c` |
| `input_optical` | `0x7ac0` |
| `input_coaxial` | `0x7a18` |

### 2. CEC Listener

Wraps `python-cec`. Registers callbacks for volume up, volume down, mute, and power key events.

Responsibilities:
- Bridge `python-cec` callbacks (non-asyncio thread) into the asyncio event loop via `call_soon_threadsafe`
- Enforce a minimum inter-event interval per command (~150ms); drop events that arrive within the window
- Map CEC key codes to logical command names
- Enqueue logical commands to the shared IR command queue

### 3. BLE GATT Server

Implemented with `bless`. Pi advertises as a BLE peripheral with a custom service.

Responsibilities:
- Advertise continuously so the side-door device can connect on press
- Accept a GATT characteristic write containing a single command byte
- Map the command byte to a logical command name
- Enqueue logical commands to the shared IR command queue
- No bonding or pairing required (accepted risk — home device, low blast radius)

Command byte encoding is defined in Design Unit 2.

### 4. IR Dispatcher

Wraps `ir-ctl`. Consumes logical commands from the shared queue and executes IR transmission.

Responsibilities:
- Consume from the shared IR command queue
- Look up the scancode from the Command Map
- Execute `ir-ctl` as a blocking subprocess call
- No state; each dispatch is independent

## Coordination

- Single asyncio event loop shared across all components
- Single IR command queue, depth ~4–8, drop-newest-on-full
- No priority between CEC and BLE input — first-in, first-served
- Queue is shallow by design; it is a concurrency buffer, not a backlog accumulator

## Interfaces

```
CEC Listener  ──► queue (logical command string)
BLE Server    ──► queue (logical command string)
queue         ──► IR Dispatcher
IR Dispatcher ──► ir-ctl subprocess
```

## Implementation Constraints

- `python-cec` delivers callbacks on a background thread; asyncio bridge is required
- `ir-ctl` subprocess call is blocking; queue decouples input receipt from IR dispatch
- BLE GATT write provides delivery confirmation (connect-on-press model, not advertise-only)

## Accepted Risks

- **BLE security**: no bonding; any nearby BLE device can send commands. Acceptable for a home environment.
- **Power toggle drift**: IR power command is a blind toggle with no state readback. Documented in project brief.
- **Input toggle ambiguity**: stateless by design. Documented in project brief.

## Readiness

**High.** Main structure and all coordination decisions are resolved. Implementation should not need to invent major design decisions.
