from typing import Any


class RecordAlreadyExists(Exception):
    def __init__(self, detail: Any = None) -> None:
        super().__init__(detail)
        self.detail = detail


class RecordNotFound(Exception):
    def __init__(self, detail: Any = None) -> None:
        super().__init__(detail)
        self.detail = detail


class AWSError(Exception): ...


class AWSUploadError(AWSError): ...


class AWSDownloadError(AWSError): ...
