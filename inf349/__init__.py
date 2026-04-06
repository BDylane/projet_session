from flask import Flask
from .models import db, Product, Order
from .services import fetch_and_store_products
from .routes import api
from .views import views
import os

def create_app():
    app = Flask(__name__)

    @app.cli.command("init-db")
    def init_db():
        db.connect(reuse_if_open=True)
        db.create_tables([Product, Order])
        db.close()
        print("La base de données a été initialisée avec succès !")

    @app.cli.command("worker")
    def worker():
        from redis import Redis
        from rq import Worker, Queue, Connection
        redis_url = os.environ.get('REDIS_URL')
        conn = Redis.from_url(redis_url)
        with Connection(conn):
            w = Worker([Queue('default')])
            w.work()

    @app.before_request
    def load_products():
        if not hasattr(app, '_products_loaded'):
            db.connect(reuse_if_open=True)
            fetch_and_store_products()
            app._products_loaded = True

    @app.after_request
    def after_request(response):
        if not db.is_closed():
            db.close()
        return response

    app.register_blueprint(api)
    app.register_blueprint(views)

    return app