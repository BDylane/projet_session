def test_create_order_success(client):
    response = client.post(
        "/order",
        json={"product": {"id": 1, "quantity": 1}},
        follow_redirects=True
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "order" in data
    order = data["order"]
    assert order["product"]["id"] == 1
    assert order["product"]["quantity"] == 1
    assert "total_price" in order
    assert "total_price_tax" in order
    assert order["product"]["quantity"] >= 1

def test_create_order_missing_product(client):
    response = client.post(
        "/order",
        json={},
        follow_redirects=True
    )
    assert response.status_code == 422
    data = response.get_json()
    assert data["errors"]["product"]["code"] == "missing-fields"

def test_create_order_missing_id(client):
    response = client.post(
        "/order",
        json={"product": {"quantity": 1}},
        follow_redirects=True
    )
    assert response.status_code == 422
    data = response.get_json()
    assert data["errors"]["product"]["code"] == "missing-fields"

def test_create_order_missing_quantity(client):
    response = client.post(
        "/order",
        json={"product": {"id": 1}},
        follow_redirects=True
    )
    assert response.status_code == 422
    data = response.get_json()
    assert data["errors"]["product"]["code"] == "missing-fields"

def test_create_order_invalid_quantity(client):
    response = client.post(
        "/order",
        json={"product": {"id": 1, "quantity": 0}},
        follow_redirects=True
    )
    assert response.status_code == 422
    data = response.get_json()
    assert data["errors"]["product"]["code"] == "missing-fields"

def test_create_order_out_of_inventory(client):
    response = client.post(
        "/order",
        json={"product": {"id": 999, "quantity": 1}},
        follow_redirects=True
    )
    assert response.status_code == 422
    data = response.get_json()
    assert data["errors"]["product"]["code"] == "out-of-inventory"

def test_get_order(client):
    post_response = client.post(
        "/order",
        json={"product": {"id": 1, "quantity": 1}},
        follow_redirects=True
    )
    assert post_response.status_code == 200
    order_id = post_response.get_json()["order"]["id"]

    get_response = client.get(f"/order/{order_id}")
    assert get_response.status_code == 200
    data = get_response.get_json()
    assert "order" in data
    order = data["order"]
    assert order["id"] == order_id
    assert order["product"]["id"] == 1
    assert order["product"]["quantity"] == 1