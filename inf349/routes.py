from flask import Blueprint, jsonify, request, redirect, url_for
import requests
from .models import Product, Order

api = Blueprint('api', __name__)

def get_tax_rate(province):
    taxes = {"QC": 0.15, "ON": 0.13, "AB": 0.05, "BC": 0.12, "NS": 0.14}
    if province not in taxes:
        raise ValueError("Invalid province")
    return taxes.get(province)

def calculate_shipping(weight_grams):
    if weight_grams <= 500: return 500
    elif weight_grams < 2000: return 1000
    else: return 2500

@api.route('/', methods=['GET'])
def get_products():
    products = Product.select()
    output = []
    for p in products:
        output.append({"id": p.id, "name": p.name, "description": p.description, "price": p.price, "in_stock": p.in_stock, "weight": p.weight, "image": p.image})
    return jsonify({"products": output}), 200

@api.route('/order', methods=['POST'])
def create_order():
    data = request.get_json()
    if (
        not data or
        "product" not in data or
        "id" not in data["product"] or
        "quantity" not in data["product"] or
        data["product"]["quantity"] < 1
    ):
        return jsonify(PRODUCTS_MISSING_FIELDS_ERROR), 422

    p_id = data["product"]["id"]
    qty = data["product"]["quantity"]

    try:
        product = Product.get_by_id(p_id)
    except Product.DoesNotExist:
        return jsonify(OUT_OF_INVENTORY_ERROR), 422

    if not product.in_stock:
        return jsonify(OUT_OF_INVENTORY_ERROR), 422
    
    new_order = Order.create(
        product=product,
        quantity=qty,
        total_price=product.price * qty,
        shipping_price=calculate_shipping(product.weight * qty)
    )

    return redirect(url_for('api.get_order', order_id=new_order.id)), 302

PRODUCTS_MISSING_FIELDS_ERROR = {
    "errors": {
        "product": {
            "code": "missing-fields",
            "name": "La création d'une commande nécessite un produit"
        }
    }
}

OUT_OF_INVENTORY_ERROR = {
    "errors": {
        "product": {
            "code": "out-of-inventory",
            "name": "Le produit demandé n'est pas en inventaire"
        }
    }
}

ORDERS_MISSING_FIELDS_ERROR = {
    "errors": {
        "order": {
            "code": "missing-fields",
            "name": "Il manque un ou plusieurs champs qui sont obligatoires"
        }
    }
}

ORDERS_MISSING_CLIENT_INFO_ERROR = {
    "errors": {
        "order": {
            "code": "missing-fields",
            "name": "Les informations du client sont nécessaire avant d'appliquer une carte de crédit"
        }
    }
}

ORDERS_ALREADY_PAID_ERROR = {
    "errors": {
        "order": {
            "code": "already-paid",
            "name": "La commande a déjà été payée"
        }
    }
}
def return_object_order(order):
    return {
        "order": {
            "id": order.id,
            "email": order.email,
            "shipping_information": {
                "country": order.country,
                "address": order.address,
                "postal_code": order.postal_code,
                "city": order.city,
                "province": order.province
            } if order.country else {},
            "credit_card": {
                "name": order.name,
                "first_digits": order.first_digits,
                "last_digits": order.last_digits,
                "expiration_year": order.expiration_year,
                "expiration_month": order.expiration_month
            } if order.name else {},
            "total_price": order.total_price,
            "total_price_tax": round(order.total_price_tax, 2) if order.total_price_tax else None,
            "transaction": {
                "id": order.transaction_id,
                "success": order.transaction_success,
                "amount_charged": order.transaction_amount_charged
            } if order.transaction_id else {},
            "paid": order.paid,
            "product": {
                "id": order.product.id,
                "quantity": order.quantity
            },
            "shipping_price": order.shipping_price
        }
    }
    
def update_shipping_info(order, data):
    order_data = data.get("order")
    ship = order_data.get("shipping_information")

    required_fields = [
        order_data.get("email"),
        ship,
        ship.get("country") if ship else None,
        ship.get("address") if ship else None,
        ship.get("postal_code") if ship else None,
        ship.get("city") if ship else None,
        ship.get("province") if ship else None,
    ]

    if any(field is None for field in required_fields):
        return jsonify(ORDERS_MISSING_FIELDS_ERROR), 422

    # Mise à jour
    order.email = order_data.get("email")
    order.address = ship.get("address")
    order.postal_code = ship.get("postal_code")
    order.city = ship.get("city")
    order.province = ship.get("province")
    order.country = ship.get("country")

    tax_rate = get_tax_rate(order.province)
    order.total_price_tax = (order.total_price + order.shipping_price) * (1 + tax_rate)

    order.save()
    return jsonify(return_object_order(order)), 200

def process_payment(order, data):
    if order.email is None or order.address is None or order.postal_code is None or order.city is None or order.province is None or order.country is None:
        return jsonify(ORDERS_MISSING_CLIENT_INFO_ERROR), 422
        
    if order.paid:
        return jsonify(ORDERS_ALREADY_PAID_ERROR), 422
    
    payment_url = "http://dimensweb.uqac.ca/~jgnault/shops/pay/"
    credit_card = data.get("credit_card")
    payload = {
        "credit_card": credit_card,
        "amount_charged": int(round(order.total_price_tax))
    }
    payloadTest = {
        "credit_card": {
            "name": "John Doe",
            "number": "4242 4242 4242 4242",
            "expiration_month": 9,
            "expiration_year": 2024,
            "cvv": "123"
        },
        "amount_charged": 10148
    }
    try:
        # response = requests.post(payment_url, json=payloadTest)    #Temporairement on utilisera un mock car pas moyen de faire fonctionner la vrai API
        response = mockRequestAPIShop(payloadTest)
        if response.status_code == 200:
            response_data = response.json()
            order.paid = True
                            
            card_data = response_data.get("credit_card")
            transaction_data = response_data.get("transaction")

            order.name = card_data.get("name")
            order.first_digits = card_data.get("first_digits")
            order.last_digits = card_data.get("last_digits")
            order.expiration_year = card_data.get("expiration_year")
            order.expiration_month = card_data.get("expiration_month")

            order.transaction_id = transaction_data.get("id")
            order.transaction_success = transaction_data.get("success")
            order.transaction_amount_charged = transaction_data.get("amount_charged")
            
            order.save()
            return jsonify(return_object_order(order)), 200
        else:
            return jsonify(response.json()), response.status_code
    except Exception:
        return jsonify(
            {
                "errors": {
                "order": {
                    "code": "service-unavailable",
                    "name": "Service de paiement indisponible"
                    }
                }
            }), 503
@api.route('/order/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    try:
        order = Order.get_by_id(order_id)
    except Order.DoesNotExist:
        return jsonify({
            "errors": {
                "order": {
                    "code": "not-found",
                    "name": "La commande demandée n'existe pas"
                }
            }
        }), 404

    data = request.get_json()

    if (
        not data or 
        ("order" not in data and "credit_card" not in data) or 
        "order" in data and "credit_card" in data
    ):
        return jsonify(ORDERS_MISSING_FIELDS_ERROR), 422

    if "order" in data :
        return update_shipping_info(order, data)

    if "credit_card" in data:
        return process_payment(order, data)
        
     
# Temporaire car pas moyen de faire fonctionner la vraie requete       
def mockRequestAPIShop(payload):

    class MockResponse:
        def __init__(self, status_code, json_data):
            self.status_code = status_code
            self._json_data = json_data

        def json(self):
            return self._json_data

    credit_card = payload.get("credit_card")
    required_fields = ["name", "number", "expiration_month", "expiration_year", "cvv"]

    if not all(field in credit_card for field in required_fields):
        return MockResponse(422, {
            "errors": {
                "credit_card": {
                    "code": "missing-fields",
                    "name": "Champs de carte de crédit manquants"
                }
            }
        })

    card_number = credit_card.get("number")

    if card_number == "4000 0000 0000 0002":
        return MockResponse(422, {
            "errors": {
                "credit_card": {
                    "code": "card-declined",
                    "name": "La carte de crédit a été déclinée"
                }
            }
        })

    if card_number == "4242 4242 4242 4242":
        return MockResponse(200, {
            "credit_card": {
                "name": credit_card.get("name"),
                "first_digits": card_number[:4],
                "last_digits": card_number[-4:],
                "expiration_year": credit_card.get("expiration_year"),
                "expiration_month": credit_card.get("expiration_month")
            },
            "transaction": {
                "id": "wgEQ4zAUdYqpr21rt8A10dDrKbfcLmqi",
                "success": True,
                "amount_charged": payload["amount_charged"]
            }
        })

    return MockResponse(400, {
        "errors": {
            "credit_card": {
                "code": "invalid-card",
                "name": "Numéro de carte invalide"
            }
        }
    })

@api.route('/order/<int:order_id>', methods=['GET'])
def get_order(order_id):
    try:
        order = Order.get_by_id(order_id)
    except Order.DoesNotExist:
        return jsonify({"error": "Commande non trouvée"}), 404

    return jsonify(return_object_order(order)), 200