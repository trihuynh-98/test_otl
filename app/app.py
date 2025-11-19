from flask import Flask
import time, random, threading
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.trace.status import Status, StatusCode

# Setup OpenTelemetry
trace.set_tracer_provider(TracerProvider(resource=Resource.create({"service.name": "test-tracing-app"})))
tracer = trace.get_tracer(__name__)
otlp_exporter = OTLPSpanExporter(endpoint="otel-collector.tracing.svc.cluster.local:4317", insecure=True)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

app = Flask(__name__)

@app.route("/")
def hello():
    with tracer.start_as_current_span("http-request"):
        time.sleep(random.uniform(0.01, 0.1))  # normal latency
        return "Hello tracing world!"

# Background function to generate spans
def generate_spans():
    while True:
        choice = random.choice(["normal", "error", "high_latency", "custom_status"])
        
        if choice == "normal":
            with tracer.start_as_current_span("normal-span") as span:
                span.set_attribute("type", "normal")
                time.sleep(random.uniform(0.01, 0.05))
        
        elif choice == "high_latency":
            with tracer.start_as_current_span("high-latency-span") as span:
                span.set_attribute("type", "high_latency")
                time.sleep(random.uniform(0.5, 1.5))  # simulate slow operation
        
        elif choice == "error":
            with tracer.start_as_current_span("error-span") as span:
                span.set_attribute("type", "error")
                span.set_status(Status(StatusCode.ERROR, "Simulated error"))
                time.sleep(random.uniform(0.01, 0.05))
        
        elif choice == "custom_status":
            with tracer.start_as_current_span("custom-status-span") as span:
                span.set_attribute("type", "custom_status")
                span.set_status(Status(StatusCode.UNSET, "Custom status"))
                time.sleep(random.uniform(0.05, 0.1))
        
        time.sleep(random.uniform(0.1, 0.5))  # wait before next span

# Run the span generator in a background thread
threading.Thread(target=generate_spans, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
