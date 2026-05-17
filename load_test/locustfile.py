from locust import HttpUser, task, between

class EcommerceUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task(2)
    def browse_products(self):
        self.client.get("/api/products", name="GET /api/products")

    @task(8)
    def cpu_heavy_request(self):
        self.client.get("/cpu?ms=250", name="GET /cpu")
