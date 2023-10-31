import json

from channels.exceptions import StopConsumer
from channels.generic.http import AsyncHttpConsumer
from django.utils.http import parse_header_parameters

from junk_drawer.cn import get_accepts


class EventsRouter:
    """
    ASGI middleware that seperates EventSource requests from normal ones.

    Namely, if the request accepts text/event-stream, SSE is used.
    """

    def __init__(self, events, web):
        self.events_handler = events
        self.web_handler = web

    def __call__(self, scope, receive, send):
        types = [t.lower() for t, _ in get_accepts(scope)]

        if 'text/event-stream' in types and scope['method'] == 'GET':
            return self.events_handler(scope, receive, send)
        else:
            return self.web_handler(scope, receive, send)


class AsyncSSEConsumer(AsyncHttpConsumer):
    # This mostly overrides AsyncHttpConsumer but it provides some useful utilities

    @property
    def last_event_id(self):
        """
        The value of the Last-Event-ID header, or None if not given.

        Raises an error if the headers haven't been received yet.
        """
        return self.scope['headers'].get('Last-Event-ID', None)

    # User API
    async def send_headers(self, *, status=200, headers=None):
        if status == 200:
            if headers is None:
                headers = [
                    (b'Content-Type', b'text/event-stream'),
                    (b'Cache-Control', b'no-cache'),
                ]
            elif isinstance(headers, dict):
                headers[b'Content-Type'] = b'text/event-stream'
                headers[b'Cache-Control'] = b'no-cache'
            else:
                headers += [
                    (b'Content-Type', b'text/event-stream'),
                    (b'Cache-Control', b'no-cache'),
                ]
        return await super().send_headers(status=status, headers=headers)

    async def accept(self):
        """
        Accept the SSE connection.

        Sends a 200 Ok with the appropriate Content-Type and such.
        """
        await self.send_headers(status=200)
        # Force sending headers immediately
        await self.send_body(b"", more_body=True)

    async def reject(self, *, status, headers=None, body=None):
        """
        Reject the SSE, sending an error and terminating the connection.
        """
        await self.send_headers(status=status, headers=headers)
        await self.send_body(body, more_body=False)
        await self.disconnect()
        raise StopConsumer()

    async def send_event(self, *, data, **fields):
        """
        Sends an event to the client, with the fields as keyword arguments.

        The data field is required.

        Other fields specified in HTML5 (section 9.2):
        * event: the event type
        * id: the event ID (used to when reconnecting)
        * retry: time to wait before reconnecting, in seconds
        """
        fields['data'] = data
        await self.send_body(
            b"\n".join(
                f"{name}: {line}".encode('utf-8')
                for name, value in fields.items()
                for line in str(value).replace('\r\n', '\n').replace('\r', '\n').split('\n')
            ) + b"\n\n",
            more_body=True,
        )

    async def send_event_json(self, *, data, **fields):
        await self.send_event(data=json.dumps(data), **fields)

    async def terminate(self):
        """
        Kill the connection from the server side.
        """
        await self.send_body(b"", more_body=False)
