import asyncio
import logging
import time

import cec

logger = logging.getLogger(__name__)

# Minimum seconds between accepted events for the same command
_DEBOUNCE_S = 0.15

# CEC user control codes -> logical command name
_CEC_KEY_MAP: dict[int, str] = {
    cec.CEC_USER_CONTROL_CODE_VOLUME_UP:   "volume_up",
    cec.CEC_USER_CONTROL_CODE_VOLUME_DOWN: "volume_down",
    cec.CEC_USER_CONTROL_CODE_MUTE:        "mute",
    cec.CEC_USER_CONTROL_CODE_POWER:       "power",
}


def start(queue: asyncio.Queue, loop: asyncio.AbstractEventLoop) -> None:
    last_event: dict[str, float] = {}

    def _on_key_press(key: int, duration: int) -> None:
        command = _CEC_KEY_MAP.get(key)
        if command is None:
            return
        now = time.monotonic()
        if now - last_event.get(command, 0.0) < _DEBOUNCE_S:
            return
        last_event[command] = now
        def _enqueue(cmd: str = command) -> None:
            try:
                queue.put_nowait(cmd)
            except asyncio.QueueFull:
                logger.debug("IR queue full, dropping %s", cmd)

        loop.call_soon_threadsafe(_enqueue)

    cec.init()
    cec.add_callback(_on_key_press, cec.EVENT_KEYPRESS)
    logger.info("CEC listener started")
