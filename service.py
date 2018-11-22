"""
Singleton service with business logic involving the database
"""
import csv
import logging
from datetime import datetime
from peewee import IntegrityError

from models import WeekBucket, Customer, Order, DATABASE

DEFAULT_CUSTOMER_FILE = 'customers.csv'
DEFAULT_ORDER_FILE = 'orders.csv'


class Service:
    """
    The singleton service
    """
    def __init__(self):
        self.logger = logging.getLogger("invitae_db")
        self.database = DATABASE
        self.database.connect()

    def __del__(self):
        self.database.close()

    def import_all_data(self):
        """
        Import all CSV data to a SQLLite database
        :return:
        """
        try:
            self.database.create_tables([Customer, Order])
            self.import_customers()
            self.import_orders()
        except IntegrityError:
            self.logger.info("Skipping import step -- data already imported")

    def import_customers(self, filename: str = DEFAULT_CUSTOMER_FILE,
                         insert_batch_size: int = 25000):
        """
        Read the customer data in the CSV file and insert it in the DB
        :param filename: The CSV file to import customers from
        :param insert_batch_size: how many rows to insert at once: default 25000
        :return:
        """
        customers = []
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
            for i, row in enumerate(reader):
                if i > 0 and i % insert_batch_size == 0:
                    Customer.insert_many(customers).execute()
                    customers = []
                customer = {
                    'id': int(row['id']),
                    'created': datetime.strptime(row['created'], "%Y-%m-%d %X"),
                }
                customers.append(customer)

        if len(customers) > 0:
            Customer.insert_many(customers).execute()

    def import_orders(self, filename: str = DEFAULT_ORDER_FILE,
                      insert_batch_size: int = 25000):
        """
        Read the order data in the CSV file and insert it in the DB
        :param filename: The CSV file to import orders from
        :param insert_batch_size: how many rows to insert at once: default 25000
        :return:
        """
        orders = []
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
            for i, row in enumerate(reader):
                if i > 0 and i % insert_batch_size == 0:
                    Order.insert_many(orders).execute()
                    orders = []
                order = {
                    'id': int(row['id']),
                    'order_number': int(row['order_number']),
                    'user_id': int(row['user_id']),
                    'created': datetime.strptime(row['created'], "%Y-%m-%d %X"),
                }
                orders.append(order)
        if len(orders) > 0:
            Order.insert_many(orders).execute()

    def get_oldest_customer_date(self) -> datetime:
        """Get the oldest customer's creation date
        """
        oldest = Customer.select().order_by(Customer.created).get()
        return oldest.created

    def get_newest_customer_date(self) -> datetime:
        """Get the newest customer's creation date
        """
        newest = Customer.select().order_by(Customer.created.desc()).get()
        return newest.created

    def get_newest_order_date(self) -> datetime:
        """Get the newest customer's creation date
        """
        newest = Order.select().order_by(Order.created.desc()).get()
        return newest.created

    def get_new_customer_ids_for(self, cohort: WeekBucket) -> {Customer}:
        """Get all Customers that are members of a given cohort
        :param cohort:
        :return:
        """
        startdate = cohort.start.datetime
        enddate = cohort.get_end().datetime
        customers = Customer.select().where(
            (Customer.created >= startdate) & (Customer.created <= enddate))[:]
        return customers

    def get_orders_for(self, customers: [int]) -> {Order}:
        """
        Get all orders for a given set of customers
        :param customers: a set of customer IDs
        :return: the Orders made
        """
        orders = Order.select()\
            .where(Order.user_id.in_(customers))\
            .order_by(Order.created)[:]
        return orders


"""
The singleton instance
"""
DBSERVICE = Service()
