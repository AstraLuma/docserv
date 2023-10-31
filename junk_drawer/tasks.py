import asyncio

from channels.consumer import AsyncConsumer


class TaskGroupMixin(AsyncConsumer):
    """
    Consumer mixin that handles additional tasks.
    """
    _tasks: asyncio.TaskGroup

    def create_task(self, coro, *, name=None, context=None):
        self._tasks.create_task(coro, name=name, context=context)

    async def __call__(self, *args):
        async with asyncio.TaskGroup() as self._tasks:
            await super().__call__(*args)
            self._tasks._abort()
