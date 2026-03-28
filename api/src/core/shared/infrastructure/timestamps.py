import datetime


def gen_string_timestamp(timestamp: datetime.datetime | None = None) -> str:
    if not timestamp:
        timestamp: datetime.datetime = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    return timestamp.strftime("%Y-%m-%d_%H:%M:%S") + f".{round(timestamp.microsecond, -4):02d}"[:3]


def gen_utc_timestamp() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
