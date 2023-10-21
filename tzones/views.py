import datetime
import zoneinfo

from django.http import Http404, HttpResponseBadRequest

from jsonish import DataResponse


def tzdata(request, zonename):
    try:
        tz = zoneinfo.ZoneInfo(zonename)
    except (ValueError, zoneinfo.ZoneInfoNotFoundError):
        raise Http404(f"Timezone {zonename!r} is not recognized")

    offset = tz.utcoffset(datetime.datetime.now())

    return DataResponse(request, 'tzinfo.html', {
        'name': tz.key,
        'utc_offset': None if offset is None else offset.total_seconds(),
        # TODO: next_change, UTC timestamp of when an expect timezone change is going to happen.
    })
