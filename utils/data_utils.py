import os
import json

CHARACTER_DATA_DIR = 'character_data/'
SHIP_INVENTORY_FILE = 'ship_inventory.json'
SHOP_INVENTORY_FILE = 'farfinder_shop.json'

def load_data(user_id):
    try:
        with open(f'{CHARACTER_DATA_DIR}{user_id}.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"characters": {}, "active_character": None}

def save_data(user_id, data):
    os.makedirs(CHARACTER_DATA_DIR, exist_ok=True)
    with open(f'{CHARACTER_DATA_DIR}{user_id}.json', 'w') as f:
        json.dump(data, f, indent=4)

def load_ship_inventory():
    try:
        with open(SHIP_INVENTORY_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'rations': 50, 'material': 50}

def save_ship_inventory(inventory):
    with open(SHIP_INVENTORY_FILE, 'w') as f:
        json.dump(inventory, f, indent=4)

def load_shop_inventory():
    """
    Loads the shop inventory from a JSON file.
    """
    if os.path.exists(SHOP_INVENTORY_FILE):
        with open(SHOP_INVENTORY_FILE, 'r') as file:
            return json.load(file)
    return []  # Return an empty list if the file doesn't exist

def save_shop_inventory(shop_inventory):
    """
    Saves the shop inventory to a JSON file.
    """
    with open(SHOP_INVENTORY_FILE, 'w') as file:
        json.dump(shop_inventory, file, indent=4)
