import asyncio
import logging

from command_map import SCANCODES

logger = logging.getLogger(__name__)

# input_toggle state: True = optical, False = coaxial
_input_state_optical = True


def _resolve_command(command: str) -> str:
    global _input_state_optical
    if command == "input_toggle":
        result = "input_optical" if _input_state_optical else "input_coaxial"
        _input_state_optical = not _input_state_optical
        return result
    return command


async def run(queue: asyncio.Queue) -> None:
    while True:
        command = await queue.get()
        resolved = _resolve_command(command)
        scancode = SCANCODES.get(resolved)
        if scancode is None:
            logger.warning("Unknown command: %s (resolved from %s)", resolved, command)
            continue
        logger.debug("Dispatching %s (scancode 0x%04x)", resolved, scancode)
        try:
            proc = await asyncio.create_subprocess_exec(
                "ir-ctl", "--send", f"--scancode=nec:0x{scancode:04x}",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await proc.communicate()
            if proc.returncode != 0:
                logger.error("ir-ctl failed for %s: %s", resolved, stderr.decode().strip())
        except Exception:
            logger.exception("ir-ctl subprocess error for %s", resolved)
