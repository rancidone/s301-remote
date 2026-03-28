# Design Unit 2 — Side-Door Device Firmware

## Problem

Design the firmware for a coin-cell-powered side-door control device that wakes on button press, connects to the Pi GATT server, writes a command byte, and disconnects. Both the firmware and the Pi-side BLE GATT schema are defined here.

## Hardware Platform

**MCU:** nRF52840 (built-in PCB trace antenna — no IPEX)

**Development path:**
1. Phase 1: SuperMini nRF52840 clone module on protoboard — validate deep sleep wakeup, GATT connect-on-press, Pi receives write
2. Phase 2: Raw nRF52840 module (e.g. E73-2G4M04S1B) on custom PCB once firmware is proven

**Toolchain:** nRF Connect SDK (Zephyr)

## BLE Interaction Model

Connect-on-press: device sleeps deeply, wakes on button press via GPIO interrupt, connects to Pi GATT server, writes command characteristic (write-with-response), disconnects. Delivery confirmed by GATT write acknowledgment. Silent drop on failed write — no retry.

## Command Byte Encoding

| Command        | Byte   |
|----------------|--------|
| `power`        | `0x01` |
| `volume_up`    | `0x02` |
| `volume_down`  | `0x03` |
| `input_toggle` | `0x04` |

Single byte, one value per command. The Pi maps these to logical command names.

## GATT Schema

- One custom 128-bit service UUID (randomly generated at design time)
- One writable characteristic (write-with-response, single byte payload)
- No bonding or pairing required

UUIDs to be generated and recorded before implementation begins. Both the firmware and the Pi-side BLE server must use the same values.

## Firmware Structure

- Deep sleep (Zephyr `PM_STATE_SOFT_OFF` or equivalent) as default state
- GPIO wakeup on button press
- On wakeup: identify which button triggered, look up command byte, connect to Pi by known service UUID, write characteristic, disconnect, return to deep sleep
- Four buttons, one per command, no multi-press or long-press behavior

## Implementation Constraints

- nRF Connect SDK (Zephyr) BLE central role for connect-on-press
- Deep sleep + GPIO wakeup sequence must be validated in Phase 1 before PCB spin
- Button debounce handled in firmware (hardware debounce not required)
- Pi GATT server must be running and advertising for delivery to succeed; silent drop otherwise

## Accepted Risks

- **Silent drop on failed write**: if Pi is not running, command is lost. Consistent with stateless design.
- **No bonding**: any nearby BLE device that knows the service UUID can trigger commands. Acceptable for home environment.

## Readiness

**High.** Hardware platform, toolchain, BLE model, command encoding, GATT schema structure, and firmware structure are all resolved. UUIDs must be generated before implementation begins but do not require further design decisions.
