from peewee import *

database = SqliteDatabase("customers.db")


class Customer(Model):
    """
    ORM model of customer
    """
    id = IntegerField(primary_key=True)
    created = DateTimeField(index=True)

    class Meta:
        database = database


class Order(Model):
    """
    ORM model of order
    """
    id = IntegerField(primary_key=True)
    order_number = IntegerField()
    user_id = ForeignKeyField(Customer, backref='orders')
    created = DateTimeField(index=True)

    class Meta:
        database = database

