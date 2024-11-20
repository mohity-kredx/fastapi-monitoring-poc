from fastapi import FastAPI
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from starlette.responses import Response
import psutil

app = FastAPI()

# Prometheus metrics
REQUEST_COUNT = Counter("app_requests_total", "Total number of requests", ["method", "endpoint"])
REQUEST_LATENCY = Histogram("app_request_latency_seconds", "Request latency in seconds", ["endpoint"])
CPU_USAGE = Gauge("app_cpu_usage_percent", "CPU usage percentage")
MEMORY_USAGE = Gauge("app_memory_usage_percent", "Memory usage percentage")

@app.middleware("http")
async def prometheus_middleware(request, call_next):
    endpoint = request.url.path
    method = request.method

    REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()
    with REQUEST_LATENCY.labels(endpoint=endpoint).time():
        response = await call_next(request)
    return response

@app.get("/")
def read_root():
    return {"message": "Hello, Prometheus and Grafana!"}

@app.get("/metrics")
def metrics():
    # Capture system resource usage
    CPU_USAGE.set(psutil.cpu_percent(interval=1))
    MEMORY_USAGE.set(psutil.virtual_memory().percent)

    # Expose metrics
    return Response(content=generate_latest(), media_type="text/plain")
