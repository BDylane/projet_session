import requests
from .models import Product, db

def fetch_and_store_products():
    # URL fournie dans l'énoncé 
    url = "http://dimensweb.uqac.ca/~jgnault/shops/products/"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json() # On transforme la réponse en dictionnaire Python
            
            # On enregistre chaque produit dans notre base de données 
            with db.atomic(): # Pour aller plus vite et sécuriser l'écriture
                for p in data['products']:
                    # On crée ou on met à jour le produit
                    Product.get_or_create(
                        id=p['id'],
                        defaults={
                            'name': p['name'],
                            'description': p['description'],
                            'price': p['price'],
                            'in_stock': p['in_stock'],
                            'weight': p['weight'],
                            'image': p['image']
                        }
                    )
            print(f"Succès : {len(data['products'])} produits importés.")
        else:
            print("Erreur lors de la récupération des produits.")
    except Exception as e:
        print(f"Erreur de connexion : {e}")