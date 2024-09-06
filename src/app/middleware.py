import time

from fastapi import Request
from opentracing import (
    InvalidCarrierException,
    SpanContextCorruptedException,
    global_tracer,
    propagation,
    tags,
)

from app.config import settings
from app.external.prometheus.metrics_updaters import (
    auth_attempts_update,
    ready_probe_status_update,
    request_count_update,
    request_duration_update,
)


async def metrics_middleware(request: Request, call_next):
    """Добавление метрик."""
    endpoint = request.url.path
    if not endpoint.startswith('/api'):
        return await call_next(request)

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    method = request.method
    status = response.status_code

    request_duration_update(method, endpoint, process_time)
    request_count_update(method, endpoint, status)

    if endpoint == '/api/healthz/ready/':
        ready_probe_status_update(status)
    elif endpoint == '/api/auth/':
        auth_attempts_update(status)

    return response


async def tracing_middleware(request: Request, call_next):
    """Добавление трассировки запросов."""
    path = request.url.path
    if not path.startswith('/api'):
        return await call_next(request)
    try:
        span_ctx = global_tracer().extract(
            propagation.Format.HTTP_HEADERS,
            request.headers,
        )
    except (InvalidCarrierException, SpanContextCorruptedException):
        span_ctx = None
    span_tags = {
        tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER,
        tags.HTTP_METHOD: request.method,
        tags.HTTP_URL: str(request.url),
    }
    with global_tracer().start_active_span(
        f'{settings.service_name}_{request.method}_{path}',
        child_of=span_ctx,
        tags=span_tags,
    ) as scope:
        response = await call_next(request)
        scope.span.set_tag(tags.HTTP_STATUS_CODE, response.status_code)
        return response
