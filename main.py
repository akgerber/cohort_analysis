import csv
import pprint
from customer import Customer
from order import Order
from datetime import datetime

pp = pprint.PrettyPrinter(indent=4)
with open('customers.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
    for row in reader:
        user_id = int(row['id'])
        created = datetime.strptime(row['created'], "%Y-%m-%d %X")  # ex: 2015-06-26 00:06:59
        customer = Customer(user_id, created)
        pp.pprint(customer)

with open('orders.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
    for row in reader:
        order_id = int(row['id'])
        order_number = int(row['order_number'])
        user_id = int(row['user_id'])
        created = datetime.strptime(row['created'], "%Y-%m-%d %X")  # ex: 2015-06-26 00:06:59
        order = Order(order_id, order_number, user_id, created)
        pp.pprint(order)
