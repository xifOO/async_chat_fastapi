import time
from typing import Awaitable, Callable

from fastapi import Request
from prometheus_client import Counter, Gauge, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from starlette.types import ASGIApp

INFO = Gauge("http_app_info", "FastAPI application information.", ["app_name"])

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total count of requests by method, path and status_code.",
    ["method", "path", "status_code", "app_name"],
)

RESPONSE_COUNT = Counter(
    "http_responses_total",
    "Total count of response by method, path and status codes.",
    ["method", "path", "status_code", "app_name"],
)

REQUESTS_PROCESSING_TIME = Histogram(
    "http_requests_duration_seconds",
    "Histogram of requests processing time by path (in seconds).",
    ["method", "path", "app_name"],
)

EXCEPTIONS = Counter(
    "http_exceptions_total",
    "Total count of exceptions raised by path and exception type.",
    ["method", "path", "exception_type", "app_name"],
)

REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Gauge of requests by method and path currently being processed.",
    ["method", "path", "app_name"],
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, app_name: str) -> None:
        super().__init__(app)
        self.app_name = app_name
        INFO.labels(app_name=self.app_name).inc()

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        method = request.method
        path = request.url.path

        REQUESTS_IN_PROGRESS.labels(
            method=method, path=path, app_name=self.app_name
        ).inc()
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except BaseException as e:
            status_code = HTTP_500_INTERNAL_SERVER_ERROR
            EXCEPTIONS.labels(
                method=method,
                path=path,
                exception_type=type(e).__name__,
                app_name=self.app_name,
            ).inc()
            raise e
        else:
            status_code = response.status_code
            after = time.perf_counter()
            status_code = response.status_code

            REQUESTS_PROCESSING_TIME.labels(
                method=method, path=path, app_name=self.app_name
            ).observe(after - start)
        finally:
            REQUEST_COUNT.labels(
                method=method,
                path=path,
                status_code=status_code,  # type: ignore[reportPossiblyUnboundVariable]
                app_name=self.app_name,
            ).inc()
            RESPONSE_COUNT.labels(
                method=method,
                path=path,
                status_code=status_code,  # type: ignore[reportPossiblyUnboundVariable]
                app_name=self.app_name,
            ).inc()
            REQUESTS_IN_PROGRESS.labels(
                method=method, path=path, app_name=self.app_name
            ).dec()
        return response
