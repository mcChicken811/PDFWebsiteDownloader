import asyncio


# act as a security of a gate to access code in the with statement
# asynchronously, once it is locked for a set time, all code attempting to enter is set on await halt
# until the lock is off
class AsyncTimedLock:
    def __init__(self) -> None:
        self._is_paused = asyncio.Event()
        self._is_paused.set()

    async def __aenter__(self):
        await self._is_paused.wait()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    # lock the lock in the current async task for a fixed duration
    # which both lock the current task for the fixed duration and lock all taskts entering until
    # the duration had passed
    # if locking when it is locked, simply wait until it is unlocked
    # duration is in seconds
    async def lock(self, duration: float):
        if self._is_paused.is_set():
            self._is_paused.clear()
            await asyncio.sleep(duration)
            self._is_paused.set()
        else:
            await self._is_paused.wait()