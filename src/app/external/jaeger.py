from jaeger_client.config import Config
from opentracing import Tracer

from app.config import settings


def initialize_jaeger_tracer() -> Tracer:
    """Инициализация Jaeger."""
    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'local_agent': {
                'reporting_host': settings.jaeger_agent_host,
                'reporting_port': int(settings.jaeger_agent_port),
            },
            'logging': True,
        },
        service_name=settings.service_name,
        validate=True,
    )
    tracer = config.initialize_tracer()
    if tracer is None:
        raise RuntimeError('Jaeger tracer is not initialized')

    return tracer
