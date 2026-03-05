def test_order_total_price_and_tax(client):
    # 1️⃣ Récupérer les produits depuis l'API
    products_response = client.get("/")
    assert products_response.status_code == 200
    products = products_response.get_json()["products"]

    # Sélectionner le produit id=1
    product_info = next(p for p in products if p["id"] == 1)
    product_weight = product_info["weight"]

    # 2️⃣ Créer la commande avec 2 unités du produit
    post_response = client.post(
        "/order",
        json={"product": {"id": 1, "quantity": 2}},
        follow_redirects=True
    )
    assert post_response.status_code == 200
    order_id = post_response.get_json()["order"]["id"]

    # 3️⃣ Ajouter email et infos de livraison
    put_response = client.put(
        f"/order/{order_id}",
        json={
            "order": {
                "email": "jgnault@uqac.ca",
                "shipping_information": {
                    "country": "Canada",
                    "address": "201, rue Président-Kennedy",
                    "postal_code": "G7X 3Y7",
                    "city": "Chicoutimi",
                    "province": "QC"
                }
            }
        },
        follow_redirects=True
    )
    assert put_response.status_code == 200
    order = put_response.get_json()["order"]

    # 4️⃣ Vérification des infos client
    assert order["email"] == "jgnault@uqac.ca"
    assert order["shipping_information"]["province"] == "QC"

    # 5️⃣ Vérification que total_price_tax >= total_price
    assert order["total_price_tax"] >= order["total_price"]

    # 6️⃣ Vérification du shipping_price selon le poids
    quantity = order["product"]["quantity"]
    total_weight = product_weight * quantity
  # calculer shipping_price en centimes pour matcher l'API
    if total_weight <= 500:
        expected_shipping = 5 * 100
    elif total_weight <= 2000:
        expected_shipping = 10 * 100
    else:
        expected_shipping = 25 * 100

    assert order["shipping_price"] == expected_shipping