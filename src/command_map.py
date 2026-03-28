# Logical command name -> NEC scancode
SCANCODES: dict[str, int] = {
    "power":         0x7E2A,
    "volume_up":     0x7A1A,
    "volume_down":   0x7A1B,
    "mute":          0x7A1C,
    "input_optical": 0x7AC0,
    "input_coaxial": 0x7A18,
}

# BLE command byte -> logical command name
# input_toggle is resolved by the dispatcher using its stateful toggle
BLE_COMMANDS: dict[int, str] = {
    0x01: "power",
    0x02: "volume_up",
    0x03: "volume_down",
    0x04: "input_toggle",
}
