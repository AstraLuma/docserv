import asyncio
from datetime import datetime

from junk_drawer.sse import AsyncSSEConsumer
from junk_drawer.tasks import TaskGroupMixin


class PlainFeed(TaskGroupMixin, AsyncSSEConsumer):

    async def connect(self, body):
        await self.accept()
        self.create_task(self._time_loop())

    async def _time_loop(self):
        try:
            while True:
                await self.send_event(data=datetime.now().isoformat())
                await asyncio.sleep(1)
        finally:
            await self.terminate()
