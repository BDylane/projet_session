from flask import Flask
from .models import db, Product, Order
from .services import fetch_and_store_products

def create_app():
    app = Flask(__name__)

    @app.cli.command("init-db")
    def init_db():
        db.connect(reuse_if_open=True)
        db.create_tables([Product, Order])
        db.close()
        print("La base de données a été initialisée avec succès !")

    @app.before_first_request
    def load_products():
        db.connect(reuse_if_open=True)
        fetch_and_store_products()
        db.close()

    @app.after_request
    def after_request(response):
        if not db.is_closed():
            db.close()
        return response

    from .routes import api
    app.register_blueprint(api)

    return app