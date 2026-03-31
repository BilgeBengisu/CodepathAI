class MenuItem:
    def __init__(self, name: str, price: float, category: str, popularity_rating: float):
        self.name = name
        self.price = price
        self.category = category
        self.popularity_rating = popularity_rating


class Order:
    def __init__(self):
        self.selected_items: list[MenuItem] = []

    def compute_total(self) -> float:
        return sum(item.price for item in self.selected_items)


class Menu:
    def __init__(self):
        self.items: list[MenuItem] = []

    def add_item(self, item: MenuItem):
        self.items.append(item)

    def filter_by_category(self, category: str) -> list[MenuItem]:
        return [item for item in self.items if item.category == category]


class Customer:
    def __init__(self, name: str):
        self.name = name
        self.purchase_history: list[Order] = []

    def verify_user(self) -> bool:
        return bool(self.name)

    def add_to_history(self, order: Order):
        self.purchase_history.append(order)
