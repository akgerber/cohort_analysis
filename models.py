"""
Models of domain objects
"""
import arrow
from peewee import SqliteDatabase, Model, IntegerField, ForeignKeyField, \
    DateTimeField

DATABASE = SqliteDatabase("customers.db")


class BaseModel(Model):
    """
    Base model with shared attributes
    """
    class Meta:
        """
        Metadata for Peewee
        """
        database = DATABASE


class Customer(BaseModel):
    """
    ORM model of customer
    """
    id = IntegerField(primary_key=True)
    created = DateTimeField(index=True)


class Order(BaseModel):
    """
    ORM model of order
    """
    id = IntegerField(primary_key=True)
    order_number = IntegerField()
    user_id = ForeignKeyField(Customer, backref='orders')
    created = DateTimeField(index=True)


class WeekBucket:
    """A weeklong bucket, extending from `start` for 7 days. Not persisted.
    """
    def __init__(self, start: arrow):
        self.start = start

    def get_end(self):
        """
        Return the datetime of the end of the week
        :return: the datetime of the end of the week
        """
        return self.start.shift(weeks=+1)

    def __eq__(self, other):
        return other.start == self.start
