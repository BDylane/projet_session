def test_create_order_missing_fields(client):
    response = client.post("/order", json={})

    assert response.status_code == 422
    assert response.json["errors"]["product"]["code"] == "missing-fields"