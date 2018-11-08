import csv
import pprint
from datetime import datetime


class Customer:
    def __init__(self, customer_id: int, created: datetime):
        self.id = customer_id
        self.created = created


pp = pprint.PrettyPrinter(indent=4)
with open('customers.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
    for row in reader:
        customer_id = int(row['id'])
        created = datetime.strptime(row['created'], "%Y-%m-%d %X")  # ex: 2015-06-26 00:06:59
        customer = Customer(customer_id, created)
        pp.pprint(customer)

