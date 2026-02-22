import pytest
# On utilise le nom du dossier 'inf349' explicitement
from inf349 import create_app
from inf349.models import db, Product, Order

@pytest.fixture
def app():
    app = create_app()
    app.config.update({"TESTING": True})
    
    # Sécurité pour la base de données
    if db.is_closed():
        db.connect()
        
    db.create_tables([Product, Order])
    
    # On prépare un produit pour les tests
    Product.get_or_create(
        id=1, 
        defaults={
            'name': "Produit Test", 
            'description': "Test", 
            'price': 1000, 
            'in_stock': True, 
            'weight': 100, 
            'image': ""
        }
    )
    
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_get_products(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"products" in response.data

def test_create_order(client):
    data = {"product": {"id": 1, "quantity": 2}}
    response = client.post('/order', json=data)
    assert response.status_code == 302

def test_order_wrong_product(client):
    # On teste le produit 999 qui n'existe pas
    data = {"product": {"id": 999, "quantity": 1}}
    response = client.post('/order', json=data)
    # Maintenant que routes.py est corrigé avec le try/except, 
    # cela devrait renvoyer 422 sans faire planter le test
    assert response.status_code == 422