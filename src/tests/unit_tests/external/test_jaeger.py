from opentracing import Tracer

from app.external.jaeger import initialize_jaeger_tracer


def test_initialize_jaeger_tracer():
    tracer = initialize_jaeger_tracer()

    assert isinstance(tracer, Tracer)
