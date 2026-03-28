# HDMI ARC Board — Hardware Design

## Design Unit

`arc-audio-routing/hdmi-board-hardware`

## Problem

TV audio must reach the Pi as an ALSA I2S capture device. HDMI ARC carries audio on HEAC+ (pin 14) as a biphase-coded S/PDIF signal. A custom PCB mounts directly on the Pi's 40-pin GPIO header, receives the HDMI ARC connector from the TV, decodes audio via PCM9211, and routes CEC to a Pi GPIO.

## Proposed Solution

A custom PCB (HAT-style, direct mount on Pi 40-pin header) with:
- HDMI Type-A female connector (to TV ARC port via cable)
- PCM9211 (TI, LQFP-48) receiving HEAC+ and outputting I2S
- 24.576 MHz crystal for PCM9211 system clock
- CEC line routed to Pi GPIO 17 via `cec-gpio` kernel driver
- 40-pin female header mating directly to Pi GPIO header
- Pi HAT mounting holes

---

## PCM9211 Circuit

**Package:** LQFP-48, 7mm × 7mm, 0.5mm pitch, pins on all 4 sides. Sourceable as PCM9211PT on DigiKey/Mouser/LCSC.

### Audio Input — RXIN0 (HEAC+)

HEAC+ (HDMI pin 14) → 0.1µF DC blocking cap → 75Ω termination resistor to GND → RXIN0 (pin 37).

RXIN0 has a built-in coaxial amplifier. No external amplification needed. GNDRX (pin 38) to GND.

RXIN1 (pin 35) is not used. Leave unconnected or pull to GND via 75Ω.

### Audio Output (I2S to Pi via 40-pin header)

| PCM9211 Pin | Signal | Pi GPIO |
|-------------|--------|---------|
| Pin 17 DOUT | I2S data | GPIO 20 |
| Pin 18 LRCK | LR clock | GPIO 19 |
| Pin 19 BCK  | Bit clock | GPIO 18 |
| Pin 20 SCKO | System clock | not connected |

PCM9211 operates as I2S master (drives BCK and LRCK). Pi I2S controller is slave receiver. SCKO not required by Pi.

### I2C Interface (to Pi via 40-pin header)

| PCM9211 Pin | Signal | Pi GPIO |
|-------------|--------|---------|
| Pin 24 MDI/SDA | I2C data | GPIO 2 |
| Pin 25 MC/SCL  | I2C clock | GPIO 3 |
| Pin 23 MDO/ADR0 | Address bit 0 | GND (address = 0x40) |
| Pin 26 MS/ADR1  | Address bit 1 | GND (address = 0x40) |
| Pin 27 MODE | Control mode | GND (selects I2C mode) |

I2C address: 0x40 (ADR1=0, ADR0=0).

### Crystal Oscillator

24.576 MHz fundamental-mode crystal on XTI (pin 39) / XTO (pin 40).
- Series resistor on XTI: 100–500Ω (crystal-dependent; start with 220Ω)
- Load capacitors (XTI and XTO to GND): 10–30pF (crystal-dependent; start with 18pF)
- Place crystal as close to pins 39/40 as possible.

### PLL Loop Filter (FILT pin 43)

Mandatory external filter on FILT (pin 43):
- 680Ω resistor from VCC (3.3V) to FILT
- 0.068mF (68µF) capacitor from FILT to GND
- 0.0047mF (4.7µF) capacitor from FILT to GND (in parallel with 68µF)

### RST Pin

RST (pin 34) is active low with internal 50kΩ pulldown. Must be driven high for normal operation.
- 10kΩ pull-up from RST to 3.3V
- Optionally connect to a Pi GPIO for software reset capability (leave as pull-up only for initial design)

### Unused ADC Pins

ADC is not used. Tie VINL (pin 47) and VINR (pin 48) to AGNDAD. VCOM (pin 44) must have external decoupling cap (0.1µF to AGNDAD) even when ADC is unused.

---

## Power Supply

PCM9211 requires both 3.3V and 5V rails. Both sourced from Pi 40-pin header.

| Rail | Pin | Source | Decoupling |
|------|-----|--------|------------|
| VCC (pin 42) | PLL analog | Pi 3.3V (header pin 1) | 0.1µF + 4.7µF ceramic near pin |
| VDD / DVDD (pin 22) | Digital | Pi 3.3V | 0.1µF + 10µF near pin |
| VDDRX (pin 36) | Coax amplifier | Pi 3.3V | 0.1µF + 10µF near pin |
| VCCAD (pin 46) | ADC analog | Pi 5V (header pin 2) | 4.7µF + 4.7µF electrolytic near pin |

TI recommends separate 3.3V pours for each supply group (VCC, VDD, VDDRX). Use short dedicated traces from header pins to each decoupling cluster; do not daisy-chain.

AGND (pin 41), AGNDAD (pin 45), DGND (pin 21), GNDRX (pin 38): all connect to a single ground plane. Keep analog and digital return currents separated by pour geometry, not separate planes.

---

## HDMI Connector Signal Routing

| HDMI Pin | Signal | Destination |
|----------|--------|-------------|
| 13 | CEC | Pi GPIO 17 via 270Ω series; 3.3kΩ pull-up to 3.3V on board |
| 14 | HEAC+ | PCM9211 RXIN0 via 0.1µF DC block + 75Ω to GND |
| 17 | GND | Board GND |
| 18 | +5V | Not connected (TV ARC port is sink) |
| 19 | HPD | 47kΩ pull-up to 3.3V (assert device presence) |

TMDS pairs (pins 1–9), DDC (pins 15–16), and all other HDMI pins: not connected. Audio-only board.

HEAC- (pin 15 shield): tie to GND via 0Ω resistor (common practice for ARC-only boards).

### CEC Circuit Detail

HDMI pin 13 → 270Ω series → Pi GPIO 17.
3.3kΩ pull-up from the CEC node (after the 270Ω) to 3.3V on board.
Pi GPIO 17 configured as open-drain via `cec-gpio` device tree overlay.

---

## Board-to-Pi Interconnect

40-pin female header (2×20, 2.54mm pitch) mates directly with Pi GPIO header.

Signals used on the 40-pin header:

| Header Pin | Signal |
|------------|--------|
| 1 | 3.3V |
| 2 | 5V (for VCCAD) |
| 3 | GPIO 2 (SDA) |
| 5 | GPIO 3 (SCL) |
| 11 | GPIO 17 (CEC) |
| 12 | GPIO 18 (BCK / I2S BCLK) |
| 35 | GPIO 19 (LRCK / I2S LRCLK) |
| 38 | GPIO 20 (DOUT / I2S data) |
| 6, 9, 14, 20, 25, 30, 34, 39 | GND (multiple) |

Remaining header pins pass through unconnected (leave pads populated for mechanical stability).

IR blaster uses separate GPIO pins not listed here — no conflict.

---

## Board Form Factor

HAT-style direct mount on Pi 3B+:
- Board dimensions: ≤65mm × 56.5mm (Pi HAT spec)
- Mounting holes: 4× M2.5 matching Pi 3B+ pattern (58mm × 49mm)
- HDMI connector positioned at board edge for cable clearance
- 40-pin female header on bottom side, mates with Pi header

---

## Layout Notes (from TI datasheet)

- Single ground plane; partition analog and digital return current paths by pour geometry
- Decoupling caps placed as close to supply pins as possible
- Crystal placed as close to XTI/XTO (pins 39/40) as possible
- Top-layer ground pour around PCM9211 connected to main plane via multiple vias
- FILT filter components close to pin 43

---

## Tradeoffs and Unresolved Decisions

- **HPD static pull-up**: simplest approach. Some TVs may expect HPD to follow pin 18 (5V). If TV doesn't enable ARC, add dynamic HPD logic. Start with static pull-up.
- **RST tied high vs Pi GPIO**: tied high via pull-up is simplest. Software reset not required for initial design; can add Pi GPIO connection if bring-up needs it.
- **ADC powered but unused**: VCCAD must be supplied per datasheet; ADC powered down in software via I2C. Draw is ~110–250µA in power-down mode — negligible from Pi 5V rail.
- **Crystal load cap values**: 18pF is a reasonable start; exact value depends on crystal spec and PCB stray capacitance. May need adjustment if clock doesn't lock.
- **RXIN1 unused**: leave unconnected or terminate with 75Ω to GND to prevent coaxial amplifier from picking up noise.

---

## Readiness

**Signal:** high

**Rationale:** Circuit is fully specified from datasheet. All pin assignments, passive values, power supply requirements, and layout constraints are concrete and sourced from TI application data. Remaining items (exact crystal load caps, HPD behavior under real TV, CONFIG_CEC_GPIO availability) are bring-up validation, not design decisions. Board is ready for schematic capture.

