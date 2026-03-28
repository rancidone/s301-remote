import asyncio
import logging
from typing import Any

from bless import BlessServer, BlessGATTCharacteristic, GATTCharacteristicProperties, GATTAttributePermissions

from command_map import BLE_COMMANDS

logger = logging.getLogger(__name__)

SERVICE_UUID = "e4cdd921-8526-4d0c-ad03-74d7d3375d53"
CHARACTERISTIC_UUID = "eebdf60a-1f6e-4d55-af12-684c03569933"


async def run(queue: asyncio.Queue, loop: asyncio.AbstractEventLoop) -> None:
    server = BlessServer(name="yamaha-remote", loop=loop)

    def _on_write(characteristic: BlessGATTCharacteristic, **kwargs: Any) -> None:
        value = characteristic.value
        if not value:
            return
        byte = value[0]
        command = BLE_COMMANDS.get(byte)
        if command is None:
            logger.warning("Unknown BLE command byte: 0x%02x", byte)
            return
        logger.debug("BLE received command: %s (0x%02x)", command, byte)
        try:
            queue.put_nowait(command)
        except asyncio.QueueFull:
            logger.debug("IR queue full, dropping BLE command %s", command)

    server.write_request_func = _on_write

    await server.add_new_service(SERVICE_UUID)
    await server.add_new_characteristic(
        SERVICE_UUID,
        CHARACTERISTIC_UUID,
        GATTCharacteristicProperties.write,
        None,
        GATTAttributePermissions.writeable,
    )

    await server.start()
    logger.info("BLE GATT server advertising as yamaha-remote")
