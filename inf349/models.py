from peewee import *

# On crée un fichier local 'database.db' pour stocker les données 
db = SqliteDatabase('database.db')

class Product(Model):
    # Les champs du produit selon les exigences [cite: 381, 382]
    id = IntegerField(primary_key=True) # Identifiant unique [cite: 380]
    name = CharField()
    description = TextField()
    price = IntegerField() # Le prix est en cents 
    in_stock = BooleanField()
    weight = IntegerField() # En grammes
    image = CharField()

    class Meta:
        database = db
        table_name = "products"

class Order(Model):
    # Informations de la commande [cite: 100-114]
    email = CharField(null=True)
    
    # Information de livraison [cite: 141-147]
    address = CharField(null=True)
    postal_code = CharField(null=True)
    city = CharField(null=True)
    province = CharField(null=True)
    country = CharField(null=True)

    # Détails financiers [cite: 126-133]
    total_price = IntegerField(default=0)
    total_price_tax = FloatField(default=0.0)
    shipping_price = IntegerField(default=0)
    paid = BooleanField(default=False)
    
    # Informations de transaction (service de paiement) [cite: 249-253]
    transaction_id = CharField(null=True)
    
    # Un seul produit par commande pour cette étape [cite: 68]
    product = ForeignKeyField(Product, backref='orders', null=True)
    quantity = IntegerField(default=1)

    class Meta:
        database = db
        table_name = "orders"