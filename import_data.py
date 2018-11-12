import csv
import pprint
from models import Customer, Order, database
from datetime import datetime

pp = pprint.PrettyPrinter()


def import_all_data(db):
    with db:
        db.create_tables([Customer, Order])
        import_customers()
        import_orders()


def import_customers(filename: str = 'customers.csv'):
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
            pp.pprint(customer)
            customers.append(customer)

    Customer.insert_many(customers).execute()


def import_orders(filename: str = 'orders.csv'):
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
            pp.pprint(order)
            orders.append(order)

    Order.insert_many(orders).execute()


if __name__ == "__main__":
    import_all_data(database)
