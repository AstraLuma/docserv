from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.template import loader
from django.utils.http import parse_header_parameters

import json

from junk_drawer.cn import parse_accept

encoders = {
    'application/json': ('json', lambda data: json.dumps(data, cls=DjangoJSONEncoder)),
}

try:
    import msgpack
except ImportError:
    msgpack = None
else:
    encoders |= {
        'application/msgpack': ('msgpack', msgpack.dumps),
        'application/x-msgpack': ('msgpack', msgpack.dumps),
        'application/vnd.msgpack': ('msgpack', msgpack.dumps),
    }

try:
    import yaml
except ImportError:
    yaml = None
else:
    encoders |= {
        # FIXME: Use django dumper
        'application/yaml': ('yaml', yaml.safe_dump),
    }

DEFAULT_ENCODING = 'application/json'


class HtmlSerializer:
    def __init__(self, request, template):
        self.request = request
        self.template = template

    def __call__(self, data):
        if isinstance(data, list):
            context = {'objects': data}
        elif isinstance(data, dict):
            context = data
        else:
            context = {'object': data}
        return loader.render_to_string(self.template, context, self.request)


def _full_encoders(request, html_template):
    return encoders | {
        'text/html': (None, HtmlSerializer(request, html_template)),
    }


class DataResponse(HttpResponse):
    def __init__(
        self,
        request,
        template,
        data,
        safe=True,
        *,
        status=200,
        headers=None,
    ):
        headers = headers or {}
        encoders = _full_encoders(request, template)

        if safe and not isinstance(data, dict):
            raise TypeError(
                "In order to allow non-dict objects to be serialized set the "
                "safe parameter to False."
            )

        # Perform Content-Negotiation
        if 'Accept' in request.headers:
            for mtype, params in parse_accept(request.headers['Accept']):
                if mtype in encoders:
                    break
                elif mtype == '*/*':
                    mtype = DEFAULT_ENCODING
                    break
            else:
                # No valid representations
                # For browser-oriented stuff, just returning HTML would probably
                # be the right choice. But this is API primarily, so let's bomb
                # instead of returning something unexpected.
                super().__init__(
                    status=406,
                    headers={'Content-Type': 'text/plain'},
                    content='\n'.join(encoders.keys()).encode('ascii')
                )
                return
        else:
            mtype = DEFAULT_ENCODING

        _, dumps = encoders[mtype]

        # Actually dump data
        content = dumps(data)
        if isinstance(content, str):
            content = content.encode('utf-8')
        headers['Content-Type'] = mtype

        super().__init__(content=content, headers=headers, status=status)
