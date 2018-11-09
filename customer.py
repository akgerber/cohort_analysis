from datetime import datetime


class Customer:
    def __init__(self, user_id: int, created: datetime):
        self.id = user_id
        self.created = created

