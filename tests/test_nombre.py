def test_get_root_returns_50_products(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert "products" in data
    assert isinstance(data["products"], list)
    assert len(data["products"]) == 50
    for product in data["products"]:
        assert all(key in product for key in ["id", "name", "description", "price", "weight", "in_stock", "image"])