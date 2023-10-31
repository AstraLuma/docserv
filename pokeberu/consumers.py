import asyncio
from datetime import datetime

from junk_drawer.sse import AsyncSSEConsumer


class PlainFeed(AsyncSSEConsumer):
    async def handle(self, body):
        await self.accept()
        while True:
            await self.send_event(data=datetime.now().isoformat())
            await asyncio.sleep(1)
