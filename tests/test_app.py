import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_products_returns_all_products():
    response = client.get("/api/products")
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert len(data["products"]) == 3
    ids = {p["id"] for p in data["products"]}
    assert ids == {1, 2, 3}


def test_checkout_valid_product():
    response = client.post("/api/checkout", json={"product_id": 1, "quantity": 2})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "created"
    assert data["product"] == "Laptop"
    assert data["quantity"] == 2
    assert data["total"] == 750000 * 2


def test_checkout_invalid_product():
    response = client.post("/api/checkout", json={"product_id": 999, "quantity": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert "not found" in data["reason"]
