from peewee import *

database = peewee.SqliteDatabase("customers.db")

class Customer:
    """
    ORM model of customer
    """
    id = IntegerField(primary_key=True)
    created = DateTimeField()

class Order:
    """
    ORM model of order
    """
    id = IntegerField(primary_key=True)
    order_number = IntegerField()
    user_id = ForeignKeyField(Customer, backref='orders')
    created = DateTimeField()
