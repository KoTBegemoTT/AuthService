from typing import Final

from prometheus_client import Counter, Gauge, Histogram

SERVICE_PREFIX: Final[str] = 'auth'
REQUEST_COUNT = Counter(
    name=f'{SERVICE_PREFIX}_request_count',
    documentation='Total number of requests',
    labelnames=['method', 'endpoint', 'status'],
)
REQUEST_DURATION = Histogram(
    name=f'{SERVICE_PREFIX}_request_duration',
    documentation='Time spent processing request',
    labelnames=['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)
READY_PROBE_STATUS = Gauge(
    name=f'{SERVICE_PREFIX}_ready_probe_status',
    documentation='Ready probe status (1 = ready, 0 = not ready)',
)
AUTH_ATTEMPTS = Counter(
    name=f'{SERVICE_PREFIX}_auth_attempts',
    documentation='Number of authentication attempts success/failure',
    labelnames=['outcome'],
)
