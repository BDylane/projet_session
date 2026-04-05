import requests
from .models import Product, db

def fetch_and_store_products():
    if not db.table_exists('products'):
        print("La table 'products' n'existe pas.")
        return
    
    url = "https://dimensweb.uqac.ca/~jgnault/shops/products/"
    
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        print(f"URL finale: {response.url}")
        print(f"Contenu brut (100 premiers chars): {repr(response.content[:100])}")
        if response.status_code == 200:
            data = response.json() # On transforme la réponse en dictionnaire Python
            
            # On enregistre chaque produit dans notre base de données 
            with db.atomic():
                for p in data['products']:
                    # Nettoyer les caractères NUL de tous les champs string
                    clean = {k: v.replace('\x00', '') if isinstance(v, str) else v for k, v in p.items()}
                    
                    Product.insert(
                        id=clean['id'],
                        name=clean['name'],
                        description=clean['description'],
                        price=clean['price'],
                        in_stock=clean['in_stock'],
                        weight=clean['weight'],
                        image=clean['image']
                    ).on_conflict_ignore().execute()
        else:
            print("Erreur lors de la récupération des produits.")
    except Exception as e:
        print(f"Erreur de connexion : {e}")