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


class Cohort:
    """A weeklong bucket, extending from `start` for 7 days. Not persisted.
    """
    def __init__(self, start: arrow):
        self.start = start

    def get_end(self):
        return self.start.shift(weeks=+1)

    def __eq__(self, other):
        return other.start == self.start
