from peewee import *

# On crée un fichier local 'database.db' pour stocker les données 
db = SqliteDatabase('database.db')

class Product(Model):
    id = IntegerField(primary_key=True)
    name = CharField()
    description = TextField()
    price = IntegerField() 
    in_stock = BooleanField()
    weight = IntegerField()
    image = CharField()

    class Meta:
        database = db
        table_name = "products"

class Order(Model):
    product = ForeignKeyField(Product, backref='orders', null=True)
    quantity = IntegerField(default=1)
    
    total_price = IntegerField(default=0)
    total_price_tax = FloatField(default=0.0)
    shipping_price = IntegerField(default=0)
    paid = BooleanField(default=False)

    # client_information
    email = CharField(null=True)
        
    # shipping_information
    country = CharField(null=True)
    address = CharField(null=True)
    postal_code = CharField(null=True)
    city = CharField(null=True)
    province = CharField(null=True)
    
    # credit_card
    name = CharField(null=True)    
    first_digits = CharField(null=True)
    last_digits = CharField(null=True)
    expiration_year = CharField(null=True)
    expiration_month = CharField(null=True)
    
    # transaction
    transaction_id = CharField(null=True)
    transaction_success = BooleanField(default=False)
    transaction_amount_charged = IntegerField(default=0)

    class Meta:
        database = db
        table_name = "orders"