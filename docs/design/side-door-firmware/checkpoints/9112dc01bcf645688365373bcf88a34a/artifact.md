# Design Unit 2 — Side-Door Device Firmware

## Status

**Not started.**

## Problem

Design the firmware and hardware for a coin-cell-powered side-door control device that communicates with the Pi GATT server to trigger Yamaha IR commands. Both the firmware and the Pi-side BLE GATT schema depend on decisions made here.

## Known Constraints

- Coin cell powered, ~1 year battery life target
- Low idle and active power consumption
- Low-latency response
- Command surface: Power, Volume Up, Volume Down, Input Toggle (Optical/Coaxial cycles)
- One button per command, no multi-press or long-press behavior
- Greenfield hardware

## BLE Model

Connect-on-press: device sleeps deeply, wakes on button press, connects to Pi GATT server, writes command characteristic, disconnects. Delivery is confirmed by the GATT write acknowledgment.

## Open Questions

- MCU/SoC selection (nRF52 series or similar)
- Command byte encoding scheme (single byte, one value per command)
- GATT service UUID and characteristic UUID
- Deep sleep current budget and expected battery life calculation
- Button debounce strategy in firmware
- Connection timeout / retry behavior on failed GATT write

## Readiness

**Low.** BLE model is chosen but hardware, firmware structure, and GATT schema are all unresolved.
