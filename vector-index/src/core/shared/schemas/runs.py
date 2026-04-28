from enum import StrEnum


class RunStatus(StrEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"
    DELETED = "DELETED"
