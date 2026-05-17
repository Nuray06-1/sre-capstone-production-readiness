from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
import math

app = FastAPI(title="E-commerce API for SRE Autoscaling Demo Demo")

PRODUCTS = [
    {"id": 1, "name": "Laptop", "price": 750000},
    {"id": 2, "name": "Headphones", "price": 45000},
    {"id": 3, "name": "Keyboard", "price": 28000},
]


class Order(BaseModel):
    product_id: int
    quantity: int = 1


HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"]
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"]
)


@app.middleware("http")
async def collect_http_metrics(request: Request, call_next):
    """
    Middleware collects metrics for all application endpoints.
    /metrics is excluded so Prometheus scraping does not distort traffic statistics.
    """
    if request.url.path == "/metrics":
        return await call_next(request)

    method = request.method
    endpoint = request.url.path
    start_time = time.perf_counter()

    try:
        response = await call_next(request)
        status_code = str(response.status_code)
    except Exception:
        status_code = "500"
        raise
    finally:
        duration = time.perf_counter() - start_time

        HTTP_REQUESTS_TOTAL.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()

        HTTP_REQUEST_DURATION_SECONDS.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

    return response


@app.get("/")
def home():
    return {"service": "ecommerce-api", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/api/products")
def get_products():
    return {"products": PRODUCTS}


@app.post("/api/checkout")
def checkout(order: Order):
    product = next((p for p in PRODUCTS if p["id"] == order.product_id), None)

    if product is None:
        return {"status": "failed", "reason": "product not found"}

    return {
        "status": "created",
        "product": product["name"],
        "quantity": order.quantity,
        "total": product["price"] * order.quantity,
    }


@app.get("/cpu")
def cpu_load(ms: int = 250):
    """
    Artificial CPU-heavy endpoint used only for load testing HPA.
    """
    end = time.time() + ms / 1000
    value = 0.0
    i = 1

    while time.time() < end:
        value += math.sqrt(i % 1000) * math.sin(i)
        i += 1

    return {
        "status": "ok",
        "work_ms": ms,
        "iterations": i,
        "value": round(value, 3)
    }


@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )