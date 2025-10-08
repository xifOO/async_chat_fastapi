from enum import Enum


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    BEARER = "bearer"


class AttachmentType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    FILE = "file"


class IncludeParams(str, Enum):
    PARTICIPANTS = "participants"