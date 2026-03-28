import uuid

from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.types import BINARY, TypeDecorator


def gen_uuid() -> bytes:
    return uuid.uuid4().bytes


class UUID(TypeDecorator):
    impl = BINARY(16)
    cache_ok = True

    def process_bind_param(self, value: uuid.UUID | str | None, dialect: Dialect):  # noqa: ARG002
        """
        When data is sent to database
        """
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return value.bytes
        if isinstance(value, bytes):
            return value
        raise TypeError(f"UUID or bytes required, found {type(value)}")

    def process_result_value(self, value: bytes | None, dialect: Dialect):  # noqa: ARG002
        """
        When data is received from database
        """
        if value is None:
            return None
        return uuid.UUID(bytes=value)
