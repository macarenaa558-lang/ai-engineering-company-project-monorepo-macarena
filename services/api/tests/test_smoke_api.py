"""Pruebas de humo de la API integrada (base SQLite y datos temporales)."""

import uuid


def test_auth_flow(client):
    email = f"smoke-{uuid.uuid4().hex[:6]}@example.com"
    password = "Password123"

    assert client.post(
        "/users", json={"email": email, "password": password, "name": "Smoke"}
    ).status_code in (200, 201)

    bad = client.post("/auth/login", data={"username": email, "password": "mala"})
    assert bad.status_code == 401

    login = client.post("/auth/login", data={"username": email, "password": password})
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    assert client.get("/auth/me", headers=headers).json()["email"] == email
    assert client.get("/auth/me").status_code == 401
    assert client.put(
        "/profiles/me", json={"name": "Nuevo"}, headers=headers
    ).status_code == 200


def test_suppliers_require_auth_and_crud(client, auth_headers):
    assert client.get("/suppliers").status_code == 401

    payload = {
        "name": "Proveedor Test",
        "country": "Colombia",
        "categories": ["carne"],
        "rate_per_unit": 10.5,
        "currency": "COP",
        "status": "active",
    }
    created = client.post("/suppliers", json=payload, headers=auth_headers)
    assert created.status_code in (200, 201), created.text
    supplier_id = created.json()["id"]

    listed = client.get("/suppliers", headers=auth_headers).json()
    assert any(item["id"] == supplier_id for item in listed)

    rated = client.patch(
        f"/suppliers/{supplier_id}/rate",
        json={"rate_per_unit": 12},
        headers=auth_headers,
    )
    assert rated.json()["rate_per_unit"] == 12

    assert client.delete(
        f"/suppliers/{supplier_id}", headers=auth_headers
    ).status_code in (200, 204)


def test_inventory_stock_is_consistent(client, auth_headers):
    assert client.post("/inventory/products", json={}).status_code == 401

    product = client.post(
        "/inventory/products",
        json={
            "name": "Carne molida",
            "sku": f"SKU-{uuid.uuid4().hex[:6]}",
            "unit": "kg",
            "category": "meat",
            "country": "CO",
        },
        headers=auth_headers,
    )
    assert product.status_code in (200, 201), product.text
    product_id = product.json()["id"]

    assert client.post(
        "/inventory/orders/inbound",
        json={
            "ingredient_id": product_id,
            "quantity": 10,
            "supplier_name": "Proveedor Test",
            "location_id": 1,
        },
        headers=auth_headers,
    ).status_code in (200, 201)

    assert client.post(
        "/inventory/orders/outbound",
        json={
            "ingredient_id": product_id,
            "quantity": 4,
            "reason": "consumption",
            "location_id": 1,
        },
        headers=auth_headers,
    ).status_code in (200, 201)

    stock = client.get(
        f"/inventory/products/{product_id}", headers=auth_headers
    ).json()["current_stock"]
    assert stock == 6

    too_much = client.post(
        "/inventory/orders/outbound",
        json={
            "ingredient_id": product_id,
            "quantity": 999,
            "reason": "waste",
            "location_id": 1,
        },
        headers=auth_headers,
    )
    assert too_much.status_code in (400, 409, 422)


def test_incident_manager(client, auth_headers):
    created = client.post(
        "/api/incidents",
        json={
            "title": "Falla",
            "description": "Horno roto",
            "category": "equipment_failure",
            "origin": "branch",
            "branch": "central",
        },
        headers=auth_headers,
    )
    assert created.status_code in (200, 201), created.text
    incident_id = created.json()["id"]

    moved = client.patch(
        f"/api/incidents/{incident_id}/status",
        json={"status": "in_progress"},
        headers=auth_headers,
    )
    assert moved.status_code == 200

    assert client.get("/api/incidents/summary", headers=auth_headers).status_code == 200


def test_incident_analysis_and_export(client, upload, auth_headers, sample_csv):
    analysis = upload(sample_csv)
    assert analysis.status_code == 200
    body = analysis.json()
    assert (body["total_records"], body["valid_records"], body["invalid_records"]) == (
        100,
        96,
        4,
    )
    assert "invalid_status" in body["error_counts"]

    assert upload(b"a,b", "x.txt").status_code == 400
    assert upload(b"a,b\n1,2\n", "x.csv").status_code == 400

    exported = client.get("/api/incidents/results/export", headers=auth_headers)
    assert exported.status_code == 200
    assert "total_records,100" in exported.text
