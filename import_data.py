import csv
import pprint
from models import Customer, Order, database
from datetime import datetime

pp = pprint.PrettyPrinter()


def import_customers(filename:str='customers.csv'):
    customers = []
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            customer = {
                'id': int(row['id']),
                'created': datetime.strptime(row['created'], "%Y-%m-%d %X"),
            }
            pp.pprint(customer)
            customers.append(customer)

    Customer.insert_many(customers).execute()


def import_orders(filename:str='orders.csv'):
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
            pp.pprint(order)
            orders.append(order)

    Order.insert_many(orders).execute()


if __name__ == "__main__":
    with database:
        database.create_tables([Customer, Order])
        import_customers()
        import_orders()


