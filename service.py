"""
Singleton service with business logic involving the database
"""
import csv
from datetime import datetime
from peewee import fn


from models import WeekBucket, Customer, Order, database


class Service:
    def __init__(self):
        self.database = database
        self.database.connect()

    def __del__(self):
        self.database.close()

    def import_all_data(self):
        self.database.create_tables([Customer, Order])
        self.import_customers()
        self.import_orders()

    def import_customers(self, filename: str = 'customers.csv'):
        """Read the customer data in the specified CSV file and insert it in the DB
        """
        customers = []
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
            for row in reader:
                customer = {
                    'id': int(row['id']),
                    'created': datetime.strptime(row['created'], "%Y-%m-%d %X"),
                }
                customers.append(customer)

        Customer.insert_many(customers).execute()

    def import_orders(self, filename: str = 'orders.csv'):
        """Read the order data in the specified CSV file and insert it in the DB
        """
        orders = []
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
            for row in reader:
                order = {
                    'id': int(row['id']),
                    'order_number': int(row['order_number']),
                    'user_id': int(row['user_id']),
                    'created': datetime.strptime(row['created'], "%Y-%m-%d %X"),
                }
                orders.append(order)

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

    def get_orders_for(self, week: WeekBucket, customers: [int]) -> {Order}:
        """
        Get all orders for a given set of customers in a given week
        :param week: the week
        :param customers: a set of customer IDs
        :return: the Orders made
        """
        startdate = week.start.datetime
        enddate = week.get_end().datetime
        orders = Order .select().where(
            (Order.created >= startdate) & (Order.created <= enddate) &
            Order.user_id.in_(customers))[:]
        return orders

    def get_order_count_for(self, week: WeekBucket, customers: [int]) -> int:
        """
        Get the count of all orders for a given set of customers in a given week
        :param week: the week
        :param customers: a set of customer IDs
        :return: the count of Orders made
        """
        startdate = week.start.datetime
        enddate = week.get_end().datetime
        count = Order.select(fn.COUNT(Order.id).alias('orders')).where(
            (Order.created >= startdate) & (Order.created < enddate) &
            Order.user_id.in_(customers)).get()
        return count.orders

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

    def get_first_orders_for(self, customers: [int]) -> {Order}:
        """
        Get all orders for a given set of first customers
        :param customers: a set of customer IDs
        :return: the Orders made
        """
        orders = Order.select(fn.MIN(Order.created).alias('firstorder'), Order.user_id)\
            .where(Order.user_id.in_(customers))\
            .distinct()\
            .order_by(Order.firstorder)[:]
        return orders


"""
The singleton instance
"""
service = Service()

