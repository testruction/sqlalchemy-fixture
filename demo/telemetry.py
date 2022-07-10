from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource

from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor, BatchSpanProcessor

from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

from opentelemetry.sdk.extension.aws.trace import AwsXRayIdGenerator

def init_tracer(args):
    """ Tracing configuration """
    resource = Resource.create(attributes={"service.namespace": "com.cdpq.studiosd",
                                           "service.name": "studiosd-webdemo"})
    
    trace.set_tracer_provider(TracerProvider(id_generator=AwsXRayIdGenerator(),
                                             resource=resource))

    jaeger_exporter = JaegerExporter()
    jaeger_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(jaeger_processor)

    otlp_exporter = OTLPSpanExporter()
    otlp_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(otlp_processor)

    if args.trace_stdout:
        trace.get_tracer_provider().add_span_processor(
            SimpleSpanProcessor(ConsoleSpanExporter()))
