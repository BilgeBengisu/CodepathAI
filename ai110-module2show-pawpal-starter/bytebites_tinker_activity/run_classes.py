from models import MenuItem, Order, Menu, Customer

# Create menu items
burger = MenuItem('Burger', 8.99, 'Entree', 4.5)
fries = MenuItem('Fries', 2.99, 'Side', 4.2)
soda = MenuItem('Soda', 1.49, 'Drink', 3.8)

print('--- MenuItem ---')
print(f'name: {burger.name}, price: {burger.price}, category: {burger.category}, popularity_rating: {burger.popularity_rating}')

# Create a menu and add items
menu = Menu()
menu.add_item(burger)
menu.add_item(fries)
menu.add_item(soda)

print('\n--- Menu ---')
print(f'all items: {[i.name for i in menu.items]}')
print(f"filter Entree: {[i.name for i in menu.filter_by_category('Entree')]}")
print(f"filter Side: {[i.name for i in menu.filter_by_category('Side')]}")

# Create an order
order = Order()
order.selected_items.append(burger)
order.selected_items.append(fries)

print('\n--- Order ---')
print(f'selected items: {[i.name for i in order.selected_items]}')
print(f'total: {order.compute_total()}')

# Create a customer
customer = Customer('Alice')
customer.add_to_history(order)

print('\n--- Customer ---')
print(f'name: {customer.name}')
print(f'verify_user: {customer.verify_user()}')
print(f'purchase_history orders: {len(customer.purchase_history)}')
print(f'first order total: {customer.purchase_history[0].compute_total()}')
