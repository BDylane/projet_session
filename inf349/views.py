from flask import Blueprint, render_template, request, redirect, url_for

views = Blueprint('views', __name__)

@views.route('/webapp', methods=['GET'])
def products_page():
    return render_template('products.html')

@views.route('/webapp/order/<int:order_id>', methods=['GET'])
def order_page(order_id):
    return render_template('order.html', order_id=order_id)

@views.route('/webapp/order/create', methods=['GET'])
def create_order_page():
    return render_template('order_create.html')

@views.route('/webapp/order/<int:order_id>/payment', methods=['GET'])
def payment_page(order_id):
    return render_template('payment.html', order_id=order_id)