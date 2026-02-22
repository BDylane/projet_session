from flask import Flask
from .models import db, Product, Order
from .services import fetch_and_store_products

def create_app():
    app = Flask(__name__)

    # On récupère les produits au lancement de l'application [cite: 377, 379]
    with app.app_context():
        fetch_and_store_products()

    @app.cli.command("init-db")
    def init_db():
        db.connect()
        db.create_tables([Product, Order])
        print("La base de données a été initialisée avec succès !")
    
    @app.after_request
    def after_request(response):
        db.close()
        return response

    from .routes import api
    app.register_blueprint(api)

    return app