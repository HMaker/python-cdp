import typing as t


class IEventLoop(t.Protocol):
    """Compatibility layer between asyncio and twisted's event loop"""

    async def sleep(self, delay: float) -> None:
        raise NotImplementedError
