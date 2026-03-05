import pytest
from inf349 import create_app

@pytest.fixture
def app():
    # Crée l'application normalement, sans passer d'arguments
    app = create_app()

    # Active le mode TESTING et ajoute d'autres configs si nécessaire
    app.config["TESTING"] = True
    # app.config["AUTRE_CONFIG"] = "valeur"

    yield app  # fournit l'app aux tests

@pytest.fixture
def client(app):
    return app.test_client()