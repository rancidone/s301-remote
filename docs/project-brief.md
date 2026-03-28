# Yamaha IR Control Bridge — Discovery Document

## Objective

Define a system that enables control of a Yamaha A-S301 amplifier using a Raspberry Pi by translating external control inputs into infrared (IR) commands.

---

## Problem Statement

Design a Raspberry Pi-based system that accepts HDMI-CEC control input and translates it into Yamaha A-S301 infrared commands, transmitting them reliably to the amplifier.

---

## Current State (Validated Proof of Concept)

### Hardware

* Yamaha A-S301 amplifier
* Raspberry Pi (DietPi)
* IR Receiver: VS1838B (bare component)
* IR Transmitter:

  * GPIO-driven IR LED
  * NPN transistor (2N2222, TO-18)
  * Base resistor (~1kΩ)
  * LED resistor (~100Ω)

### GPIO Configuration

* IR Receive: GPIO17 (pin 11)
* IR Transmit: GPIO18 (pin 12)

### Boot Configuration

```
dtoverlay=gpio-ir,gpio_pin=17,active_low=1
dtoverlay=gpio-ir-tx,gpio_pin=18
```

### Software

* OS: DietPi
* Tools:

  * ir-keytable (receive / decode)
  * ir-ctl (transmit)

### IR Protocol

* NEC

### Captured IR Scancodes

```
Power    0x7e2a
Optical  0x7ac0
Coaxial  0x7a18
Vol+     0x7a1a
Vol-     0x7a1b
Mute     0x7a1c
```

### Validation

* IR receive path confirmed via ir-keytable
* IR transmit path confirmed via ir-ctl
* Amplifier responds correctly to transmitted commands

---

## System Boundary

### Inputs

Primary:

* HDMI-CEC (TV remote control)

Secondary (in scope for v1):

* Low-power side-door control device

### Supported Command Surface

HDMI-CEC:

* Volume Up
* Volume Down
* Mute
* Power (toggle)

Side-Door Control Device:

* Volume Up
* Volume Down
* Power (toggle)
* Input Toggle (Optical / Coaxial)

---

## Processing

* Map incoming control events to Yamaha IR commands
* Minimal normalization (no state enforcement)
* Stateless command translation model

---

## Outputs

* IR transmission via Raspberry Pi GPIO-based emitter

---

## Intended v1 Outcomes

* Enable TV remote (via HDMI-CEC) to control:

  * Volume Up
  * Volume Down
  * Mute
  * Power (toggle)

* Enable side-door control device to control:

  * Volume Up
  * Volume Down
  * Power (toggle)
  * Input Toggle (Optical / Coaxial)

---

## Architecture Characteristics (v1)

* Stateless or near-stateless system
* Multiple input sources (CEC and side-door device)
* Parallel command paths with overlapping capabilities
* No amplifier state awareness or synchronization
* IR emission is the only actuation mechanism

---

## Constraints

* Single target device: Yamaha A-S301
* Infrared is the required output mechanism
* Raspberry Pi is colocated with amplifier
* HDMI-CEC is a primary control interface
* Secondary input device is required for v1
* No assumption of Yamaha external control API
* No assumption of state readback capability

---

## Power Handling Model

* Power is implemented as a blind IR toggle
* No verification of actual amplifier state
* No synchronization between system and amplifier state

### Known Behavior

* Possible state drift between user expectation and actual amplifier state

---

## Secondary Input Device — v1 Definition

### Command Surface

* Power (toggle)
* Volume Up
* Volume Down
* Input Toggle (cycles between Optical and Coaxial)

### Interaction Model

* One button per command
* No multi-press, long-press, or gesture-based behavior
* Input selection is a blind toggle

### Behavioral Characteristics

* Input toggle may not match actual amplifier state
* Repeated presses may be required to reach desired input

### Constraints

* Coin cell powered
* Target battery life ~1 year
* Low idle and active power consumption
* Low-latency response

---

## Risks and Edge Cases

* Power toggle drift due to lack of feedback
* Input toggle ambiguity due to stateless design
* Conflicts between CEC and side-door commands
* Rapid or repeated volume inputs may require rate handling decisions
* HDMI-CEC implementation variability across TVs

---

## Deferred Capabilities (Out of Scope for v1)

* Power state detection (e.g., optical sensing of front-panel LED)
* Web-based control interface
* Mobile application

---

## Summary

The system is a stateless command translation bridge that accepts multiple input sources and emits Yamaha IR commands. HDMI-CEC provides primary control for volume and basic operations, while a dedicated low-power side-door device ensures reliable access to power and input selection. The design prioritizes simplicity, determinism, and reliability while explicitly accepting state ambiguity as a trade-off.
