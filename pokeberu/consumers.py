import asyncio
from datetime import datetime

from junk_drawer.sse import AsyncSSEConsumer


class PlainFeed(AsyncSSEConsumer):
    task = None

    async def connect(self, body):
        await self.accept()
        self.task = asyncio.create_task(self._time_loop())

    async def _time_loop(self):
        try:
            while True:
                await self.send_event(data=datetime.now().isoformat())
                await asyncio.sleep(1)
        finally:
            await self.terminate()

    async def disconnect(self):
        print("Disconnect")
        if self.task is not None:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
