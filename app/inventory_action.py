import csv


def update_ingredient_inventory(item_name, quantity, inventory, mappings):
    item_mapping = next((m for m in mappings if m['item'] == item_name), None)
    if not item_mapping:
        return None, 200  # Skip items without mapping

    ingredients = item_mapping['ingredients']
    if not ingredients:
        return None, 200  # Skip items without ingredients

    ingredients = ingredients.split(", ")
    for ingredient in ingredients:
        name, qty = ingredient.split(": ")
        qty = int(qty)
        inventory_item = next((i for i in inventory if i['ingredient'] == name), None)
        if not inventory_item:
            return f"Ingredient '{name}' not found in inventory", 404
        new_count = int(inventory_item['count']) - (qty * quantity)
        if new_count < 0:
            return f"Not enough '{name}' in inventory to fulfill the order", 400
        inventory_item['count'] = new_count
    return None, 200

def check_inventory_availability(item_name, quantity, inventory, mappings):
    item_mapping = next((m for m in mappings if m['item'] == item_name), None)
    if not item_mapping:
        return True  # If no mapping, assume it doesn't need any ingredients

    ingredients = item_mapping['ingredients']
    if not ingredients:
        return True  # If no ingredients listed, assume it doesn't need any ingredients

    ingredients = ingredients.split(", ")
    for ingredient in ingredients:
        name, qty = ingredient.split(": ")
        qty = int(qty)
        inventory_item = next((i for i in inventory if i['ingredient'] == name), None)
        if not inventory_item or int(inventory_item['count']) < (qty * quantity):
            return False  # Not enough ingredients
    return True

def calculate_missing_ingredients(item_name, quantity, inventory, mappings):
    missing_ingredients = []
    item_mapping = next((m for m in mappings if m['item'] == item_name), None)
    if not item_mapping:
        return missing_ingredients  # No mapping, no ingredients needed

    ingredients = item_mapping['ingredients'].split(", ")
    for ingredient in ingredients:
        name, qty = ingredient.split(": ")
        qty = int(qty)
        inventory_item = next((i for i in inventory if i['ingredient'] == name), None)
        if not inventory_item:
            missing_ingredients.append({'ingredient': name, 'required': qty * quantity, 'available': 0})
        elif int(inventory_item['count']) < (qty * quantity):
            missing_ingredients.append({
                'ingredient': name,
                'required': qty * quantity,
                'available': int(inventory_item['count'])
            })
    return missing_ingredients

# Helper functions for CSV operations
def read_csv(filename):
    data = []
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data

def write_csv(filename, data):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = data[0].keys() if data else []
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in data:
            writer.writerow(item)
