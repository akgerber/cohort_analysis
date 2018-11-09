from datetime import datetime


class Customer:
    def __init__(self, user_id: int, created: datetime):
        self.id = user_id
        self.created = created

class Order:
    def __init__(self, order_id: int, order_number: int, user_id: int, created: datetime):
        self.order_id = order_id
        self.order_number = order_number
        self.user_id = user_id
        self.created = created
