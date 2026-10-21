"""Todas las rutas de inventario exigen autenticación."""

import pytest

ROUTES = [
    ("GET", "/inventory/products"),
    ("GET", "/inventory/products/1"),
    ("GET", "/inventory/orders"),
    ("POST", "/inventory/products"),
    ("POST", "/inventory/orders/inbound"),
    ("POST", "/inventory/orders/outbound"),
]


@pytest.mark.parametrize("method,path", ROUTES)
def test_inventory_requires_token(client, method, path):
    assert client.request(method, path).status_code == 401
    bad = {"Authorization": "Bearer token-invalido"}
    assert client.request(method, path, headers=bad).status_code == 401


def test_inventory_reads_work_with_token(client, auth_headers):
    assert client.get("/inventory/products", headers=auth_headers).status_code == 200
    assert client.get("/inventory/orders", headers=auth_headers).status_code == 200
    assert client.get("/inventory/products/999999", headers=auth_headers).status_code == 404
