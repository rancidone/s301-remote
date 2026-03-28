import asyncio
import logging

import cec_listener
import ir_dispatcher
import ble_server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

QUEUE_DEPTH = 6


async def _main() -> None:
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue[str] = asyncio.Queue(maxsize=QUEUE_DEPTH)

    cec_listener.start(queue, loop)
    asyncio.create_task(ble_server.run(queue, loop))
    asyncio.create_task(ir_dispatcher.run(queue))

    logger.info("yamaha-remote running")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(_main())
