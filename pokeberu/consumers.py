import asyncio
from datetime import datetime
from channels.generic.http import AsyncHttpConsumer


class EventSourceConsumer(AsyncHttpConsumer):
    """
    AsyncHttpConsumer that can produce Server-Sent Events.
    """

    @property
    def last_event_id(self):
        return self.scope['headers'].get('Last-Event-ID', None)

    async def start_stream(self):
        """
        Set up the stream.
        """
        await self.send_headers(headers=[
            (b"Cache-Control", b"no-cache"),
            (b"Content-Type", b"text/event-stream"),
            (b"Transfer-Encoding", b"chunked"),
        ])

    async def send_event(self, *, data, **fields):
        """
        Send an SSE event. Params are the event fields:

        * data: The actual data, mandatory
        * event: The name of the event
        * id: The ID of the event, related to Last-Event-ID
        * retry: reconnection time (ms)
        * (empty): Comment

        ``None`` values are interpreted as valueless fields.
        """
        fields['data'] = data
        payload = "\n".join(
            # FIXME: Handle newlines in values
            f"{k}: {v}" if v is not None else k
            for k, v in fields.items()
        ) + '\n\n'
        await self.send_body(payload.encode('utf-8'), more_body=True)

    async def end_stream(self):
        """
        Terminate stream and disconnect client.
        """
        await self.send_body(b"", more_body=False)


class PlainFeed(EventSourceConsumer):
    async def handle(self, body):
        await self.start_stream()
        while True:
            await self.send_event(data=datetime.now().isoformat())
            await asyncio.sleep(1)
