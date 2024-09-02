from fastapi import status

from app.external.prometheus.metrics import (
    AUTH_ATTEMPTS,
    READY_PROBE_STATUS,
    REQUEST_COUNT,
    REQUEST_DURATION,
)


def request_duration_update(
    method: str,
    endpoint: str,
    process_time: float,
) -> None:
    """Обновление метрики времени обработки запроса."""
    REQUEST_DURATION.labels(
        method=method,
        endpoint=endpoint,
    ).observe(process_time)


def request_count_update(
    method: str,
    endpoint: str,
    status_code: int,
) -> None:
    """Обновление метрики количества обработанных запросов."""
    REQUEST_COUNT.labels(
        method=method,
        endpoint=endpoint,
        status=status_code,
    ).inc()


def ready_probe_status_update(status_code: int) -> None:
    """Обновление метрики состояния сервиса."""
    if status_code == status.HTTP_200_OK:
        READY_PROBE_STATUS.set(1)
    else:
        READY_PROBE_STATUS.set(0)


def auth_attempts_update(status_code: int) -> None:
    """Обновление метрики количества попыток аутентификации."""
    if status_code == status.HTTP_201_CREATED:
        AUTH_ATTEMPTS.labels(outcome='success').inc()
    else:
        AUTH_ATTEMPTS.labels(outcome='failure').inc()
