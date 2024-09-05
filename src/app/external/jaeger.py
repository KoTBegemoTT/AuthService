from jaeger_client.config import Config
from opentracing import Tracer

from app.config import settings


def initialize_jaeger_tracer() -> Tracer:
    """Инициализация Jaeger."""
    config = Config(
        config={
            'sampler': {
                'type': settings.jaeger_sampler_type,
                'param': settings.jaeger_sampler_param,
            },
            'local_agent': {
                'reporting_host': settings.jaeger_agent_host,
                'reporting_port': int(settings.jaeger_agent_port),
            },
            'logging': settings.jaeger_logging,
        },
        service_name=settings.service_name,
        validate=settings.jaeger_validate,
    )
    tracer = config.initialize_tracer()
    if tracer is None:
        raise RuntimeError('Jaeger tracer is not initialized')

    return tracer
