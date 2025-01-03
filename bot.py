import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import json

# Load environment variables from the .env file
load_dotenv()

# Bot setup
TOKEN = os.getenv("DISCORD_TOKEN")
GUILDID = os.getenv("GUILDID")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Path to your JSON files where character data and ship inventory will be stored
CHARACTER_DATA_DIR = 'character_data/'
SHIP_INVENTORY_FILE = 'ship_inventory.json'

# Load character data from the JSON file
def load_data(user_id):
    try:
        with open(f'{CHARACTER_DATA_DIR}{user_id}.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"characters": {}, "active_character": None}

# Save character data to the JSON file
def save_data(user_id, data):
    os.makedirs(CHARACTER_DATA_DIR, exist_ok=True)
    with open(f'{CHARACTER_DATA_DIR}{user_id}.json', 'w') as f:
        json.dump(data, f, indent=4)

# Load the ship's inventory from the file
def load_ship_inventory():
    try:
        with open(SHIP_INVENTORY_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'rations': 50, 'waterskins': 50, 'material': 50}  # Default values

# Save the ship's inventory to the file
def save_ship_inventory(ship_inventory):
    with open(SHIP_INVENTORY_FILE, 'w') as f:
        json.dump(ship_inventory, f, indent=4)

# Command to register a new character
@bot.command()
async def register_character(ctx, character_name, character_class, species, background, description=""):
    user_id = str(ctx.author.id)
    data = load_data(user_id)

    if character_name in data["characters"]:
        await ctx.send(f"Character {character_name} already registered.")
        return

    data["characters"][character_name] = {
        "class": character_class,
        "species": species,
        "background": background,
        "level": 1,
        "description": description,
        "inventory": {'rations': 0, 'waterskins': 0, 'material': 0}  # Initialize character's inventory
    }

    save_data(user_id, data)
    await ctx.send(f"Character {character_name} registered successfully!")

# Command to switch between characters
@bot.command()
async def switch_character(ctx, character_name):
    user_id = str(ctx.author.id)
    data = load_data(user_id)

    if character_name in data["characters"]:
        data["active_character"] = character_name
        save_data(user_id, data)

        # Change nickname to match the active character
        member = ctx.author
        try:
            await member.edit(nick=character_name)
            await ctx.send(f"Switched to character {character_name} and updated your nickname!")
        except discord.Forbidden:
            await ctx.send("I don't have permission to change your nickname.")
        
    else:
        await ctx.send("Character not found. Please register the character first.")

# Command to view the active character's profile
@bot.command()
async def profile(ctx):
    user_id = str(ctx.author.id)
    data = load_data(user_id)

    active_character = data.get("active_character")
    if active_character:
        character_info = data["characters"].get(active_character)
        profile_str = (
            f"Name: {active_character}\n"
            f"Class: {character_info['class']}\n"
            f"Species: {character_info['species']}\n"
            f"Background: {character_info['background']}\n"
            f"Level: {character_info['level']}\n"
            f"Description: {character_info['description'] if character_info['description'] else 'No description set.'}"
        )
        await ctx.send(profile_str)
    else:
        await ctx.send("You don't have an active character. Please switch to one first.")

# Command to list all characters for the user
@bot.command()
async def my_characters(ctx):
    user_id = str(ctx.author.id)
    data = load_data(user_id)

    characters = data["characters"]
    character_list = [name for name in characters if name != data["active_character"]]
    await ctx.send(f"Your characters: {', '.join(character_list) if character_list else 'None'}")

# Command to set or update attributes of the active character
@bot.command()
async def set(ctx, attribute: str, *, value: str):
    user_id = str(ctx.author.id)
    data = load_data(user_id)

    active_character = data.get("active_character")
    if not active_character:
        await ctx.send("You don't have an active character. Please switch to one first.")
        return

    # Validate the attribute
    valid_attributes = ["class", "species", "background", "level", "description"]
    if attribute not in valid_attributes:
        await ctx.send(f"Invalid attribute! You can set: {', '.join(valid_attributes)}.")
        return

    # If the attribute is 'level', ensure it's a positive integer
    if attribute == "level":
        try:
            value = int(value)
            if value <= 0:
                raise ValueError("Level must be a positive integer.")
        except ValueError:
            await ctx.send("Level must be a positive integer.")
            return

    # Update the attribute
    data["characters"][active_character][attribute] = value
    save_data(user_id, data)

    await ctx.send(f"Updated {attribute} for {active_character} to: {value}.")

# Command for players to take materials from the ship (Rations, Waterskins, or Material)
@bot.command()
async def take(ctx, material: str, amount: int):
    user_id = str(ctx.author.id)
    data = load_data(user_id)

    if material not in ['rations', 'waterskins', 'material']:
        await ctx.send(f"Invalid material! Available materials: rations, waterskins, material.")
        return

    if amount <= 0:
        await ctx.send("Amount must be a positive number.")
        return

    # Load the ship inventory from the file
    ship_inventory = load_ship_inventory()
    
    if ship_inventory[material] < amount:
        await ctx.send(f"Not enough {material} on the ship!")
        return

    # Load or create character's inventory
    active_character = data.get("active_character")
    character_inventory = data["characters"].get(active_character, {}).get("inventory", {})

    # Add materials to character's inventory
    character_inventory[material] = character_inventory.get(material, 0) + amount
    ship_inventory[material] -= amount

    # Save the updated data
    save_data(user_id, data)
    save_ship_inventory(ship_inventory)

    await ctx.send(f"{active_character} took {amount} {material}(s)!")
    await ctx.send(f"Ship's {material} left: {ship_inventory[material]}")
    await ctx.send(f"{active_character}'s {material}: {character_inventory[material]}")

# Command for players to deposit materials into the ship
@bot.command()
async def deposit(ctx, material: str, amount: int):
    user_id = str(ctx.author.id)
    data = load_data(user_id)

    if material not in ['rations', 'waterskins', 'material']:
        await ctx.send(f"Invalid material! Available materials: rations, waterskins, material.")
        return

    if amount <= 0:
        await ctx.send("Amount must be a positive number.")
        return

    # Load the ship inventory from the file
    ship_inventory = load_ship_inventory()

    # Load or create character's inventory
    active_character = data.get("active_character")
    character_inventory = data["characters"].get(active_character, {}).get("inventory", {})

    if character_inventory.get(material, 0) < amount:
        await ctx.send(f"You don't have enough {material} to deposit.")
        return

    # Update inventories
    character_inventory[material] -= amount
    ship_inventory[material] += amount

    save_data(user_id, data)
    save_ship_inventory(ship_inventory)
    await ctx.send(f"{active_character} deposited {amount} {material}(s) into the ship!")

# Command to adjust the active character's inventory
@bot.command()
async def adjust(ctx, material: str, amount: int):
    user_id = str(ctx.author.id)
    data = load_data(user_id)

    active_character = data.get("active_character")
    if not active_character:
        await ctx.send("You don't have an active character. Please switch to one first.")
        return

    if material not in ['rations', 'waterskins', 'material']:
        await ctx.send(f"Invalid material! Available materials: rations, waterskins, material.")
        return

    # Get the active character's inventory
    character_inventory = data["characters"][active_character].get("inventory", {})
    character_inventory[material] = character_inventory.get(material, 0) + amount

    # Prevent negative inventory
    if character_inventory[material] < 0:
        character_inventory[material] = 0

    # Save the updated character inventory
    data["characters"][active_character]["inventory"] = character_inventory
    save_data(user_id, data)

    await ctx.send(f"Adjusted {material} for {active_character} by {amount}. New total: {character_inventory[material]}")

# Command to see the ship's inventory (admins or authorized users only)
@bot.command()
async def shipinventory(ctx):
    # Load the ship's inventory
    ship_inventory = load_ship_inventory()
    
    await ctx.send(f"Ship's Inventory:\nRations: {ship_inventory['rations']}\nWaterskins: {ship_inventory['waterskins']}\nMaterial: {ship_inventory['material']}")

@bot.command()
async def inventory(ctx):
    user_id = str(ctx.author.id)
    data = load_data(user_id)

    active_character = data.get("active_character")
    if active_character:
        character_inventory = data["characters"][active_character].get("inventory", {})
        inventory_str = (
            f"Inventory for {active_character}:\n"
            f"Rations: {character_inventory.get('rations', 0)}\n"
            f"Waterskins: {character_inventory.get('waterskins', 0)}\n"
            f"Material: {character_inventory.get('material', 0)}"
        )
        await ctx.send(inventory_str)
    else:
        await ctx.send("You don't have an active character. Please switch to one first.")

# Run the bot
bot.run(TOKEN)
