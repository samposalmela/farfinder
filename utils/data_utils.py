import os
import json

CHARACTER_DATA_DIR = 'character_data/'
SHIP_INVENTORY_FILE = 'ship_inventory.json'

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
