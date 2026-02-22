from flask import Blueprint, jsonify, request, redirect, url_for
import requests
from .models import Product, Order

api = Blueprint('api', __name__)

def get_tax_rate(province):
    taxes = {"QC": 0.15, "ON": 0.13, "AB": 0.05, "BC": 0.12, "NS": 0.14}
    return taxes.get(province, 0.0)

def calculate_shipping(weight_grams):
    if weight_grams < 500: return 500
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
    
    if not data or 'product' not in data or 'id' not in data['product'] or 'quantity' not in data['product']:
        return jsonify({"errors": {"product": {"code": "missing-fields", "name": "Produit et quantité requis"}}}), 422
    
    p_id = data['product']['id']
    qty = data['product']['quantity']

    # --- C'EST CETTE PARTIE QUI PROTÈGE LE CODE ---
    try:
        product = Product.get_by_id(p_id)
    except Product.DoesNotExist:
        return jsonify({"errors": {"product": {"code": "out-of-inventory", "name": "Le produit demandé n'existe pas"}}}), 422

    if not product.in_stock:
        return jsonify({"errors": {"product": {"code": "out-of-inventory", "name": "Hors inventaire"}}}), 422

    new_order = Order.create(
        product=product,
        quantity=qty,
        total_price=product.price * qty,
        shipping_price=calculate_shipping(product.weight * qty)
    )
    return redirect(url_for('api.get_order', order_id=new_order.id)), 302

@api.route('/order/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    try:
        order = Order.get_by_id(order_id)
    except Order.DoesNotExist:
        return jsonify({"error": "Commande non trouvée"}), 404

    data = request.get_json()
    ship = data.get('order', {}).get('shipping_information', {})
    
    order.email = data.get('order', {}).get('email')
    order.address, order.postal_code = ship.get('address'), ship.get('postal_code')
    order.city, order.province, order.country = ship.get('city'), ship.get('province'), ship.get('country')

    tax_rate = get_tax_rate(order.province)
    order.total_price_tax = (order.total_price + order.shipping_price) * (1 + tax_rate)
    order.save()
    return redirect(url_for('api.get_order', order_id=order.id)), 302

@api.route('/order/<int:order_id>/pay', methods=['POST'])
def pay_order(order_id):
    try:
        order = Order.get_by_id(order_id)
    except Order.DoesNotExist:
        return jsonify({"error": "Commande non trouvée"}), 404

    data = request.get_json()
    credit_card = data.get('order', {}).get('credit_card')

    if not credit_card or not all(k in credit_card for k in ('number', 'expiration_month', 'expiration_year', 'cvv')):
        return jsonify({"errors": {"order": {"code": "missing-fields", "name": "Carte incomplète"}}}), 422

    payment_url = "http://dimensweb.uqac.ca/~jgnault/shops/pay/"
    payload = {
        "credit_card": credit_card,
        "amount_and_currency": {"amount": int(order.total_price_tax), "currency": "cad"}
    }

    try:
        response = requests.post(payment_url, json=payload)
        if response.status_code == 200:
            res_data = response.json()
            order.paid = True
            order.transaction_id = res_data.get('transaction_id')
            order.save()
            return redirect(url_for('api.get_order', order_id=order.id)), 302
        else:
            return jsonify(response.json()), response.status_code
    except:
        return jsonify({"error": "Service de paiement indisponible"}), 503

@api.route('/order/<int:order_id>', methods=['GET'])
def get_order(order_id):
    try:
        order = Order.get_by_id(order_id)
    except Order.DoesNotExist:
        return jsonify({"error": "Commande non trouvée"}), 404

    return jsonify({
        "order": {
            "id": order.id,
            "total_price": order.total_price,
            "total_price_tax": round(order.total_price_tax, 2),
            "email": order.email,
            "paid": order.paid,
            "shipping_price": order.shipping_price,
            "transaction": {"id": order.transaction_id} if order.paid else {},
            "product": {"id": order.product.id, "quantity": order.quantity}
        }
    }), 200