import time

from fastapi import Request

from app.external.prometheus.metrics_updaters import (
    auth_attempts_update,
    ready_probe_status_update,
    request_count_update,
    request_duration_update,
)


async def metrics_middleware(request: Request, call_next):
    """Обработчик запросов."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    endpoint = request.url.path
    method = request.method
    status = response.status_code

    request_duration_update(method, endpoint, process_time)
    request_count_update(method, endpoint, status)

    if endpoint == '/healthz/ready/':
        ready_probe_status_update(status)
    elif endpoint == '/auth/':
        auth_attempts_update(status)

    return response
