import datetime
import zoneinfo

from django.http import Http404, HttpResponseBadRequest

from jsonish import DataResponse

# Some of the next two functions are magical, namely about when to round.
# Determined experimentally by Andrew Godwin, so the results are stable.
# May the wrath of Aion, Janus, Heh, and Skuld be gentle.

# Getting 100% correct results using this method appears to be the path
# to madness. Don't do it. If some future human wants to make this more
# correct, I suggest digging into zoneinfo internals and calculating this
# more directly.


def dt_avg(a: datetime.datetime, b: datetime.datetime):
    """
    Calculate the average of two datetimes.
    """
    diff = b - a
    diff = datetime.timedelta(seconds=int(diff.total_seconds() / 2))
    return a + diff


def next_dst_change(timezone) -> datetime.datetime:
    """
    Finds the next scheduled UTC offset change.

    Returns some arbitrary point in the future if now offset change is
    detected.
    """
    # Instead of calculating directly, run a binary search to find it. This is
    # because the data structures are opaque and _nobody_ provides this
    # information directly. (Trust me, I looked.)
    low = datetime.datetime.now(tz=timezone).replace(microsecond=0)
    high = low + datetime.timedelta(days=90)
    # Note that in the US, it's 4mo off and 8mo on, so a 3mo search window will
    # not miss it.
    # Europe I think it's 5mo off and 7mo on.
    if high.utcoffset() == low.utcoffset():
        # No DST change occurred, just give a default
        return high
    for i in range(24):  # Should be the number of rounds to get to a second.
        if high - low < datetime.timedelta(seconds=1):
            break
        mid = dt_avg(low, high)
        if mid.utcoffset() != low.utcoffset():
            # Offset change between low and mid
            high = mid
            continue
        else:
            # Offset change between mid and high
            low = mid
            continue
    print(f"{low} - {high}")
    return dt_avg(low, high)


def tzdata(request, zonename):
    try:
        tz = zoneinfo.ZoneInfo(zonename)
    except (ValueError, zoneinfo.ZoneInfoNotFoundError):
        raise Http404(f"Timezone {zonename!r} is not recognized")

    offset = tz.utcoffset(datetime.datetime.now())

    return DataResponse(request, 'tzinfo.html', {
        'name': tz.key,
        'utc_offset': None if offset is None else round(offset.total_seconds()),
        'next_change': round(next_dst_change(tz).timestamp()) + 10
    })
