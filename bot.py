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
        return {'rations': 50, 'material': 50}  # Default values

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
        "status": "Idle",
        "description": description,
        "inventory": {'rations': 0, 'material': 0}  # Initialize character's inventory
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
            f"Status: {character_info['status']}\n"
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

# Command for players to set their status to "Idle"
@bot.command()
async def idle(ctx):
    user_id = str(ctx.author.id)
    data = load_data(user_id)

    active_character = data.get("active_character")
    if active_character:
        # Set the status to Idle
        data["characters"][active_character]["status"] = "Idle"
        save_data(user_id, data)

        # Assign the Idle role
        member = ctx.author
        role = discord.utils.get(ctx.guild.roles, name="Idle")
        if role:
            # Remove other status roles if present
            for status in ["Exploring", "Resting"]:
                status_role = discord.utils.get(ctx.guild.roles, name=status)
                if status_role in member.roles:
                    await member.remove_roles(status_role)
            await member.add_roles(role)
            await ctx.send(f"{active_character} is now idle, and the role has been applied.")
        else:
            await ctx.send("Role 'Idle' not found. Please create it.")
    else:
        await ctx.send("You don't have an active character. Please switch to one first.")

# Command for players to set their status to "Resting"
@bot.command()
async def rest(ctx):
    user_id = str(ctx.author.id)
    data = load_data(user_id)

    active_character = data.get("active_character")
    if active_character:
        # Get the character's current inventory
        character_inventory = data["characters"][active_character].get("inventory", {})
        
        # Check if the character has enough rations
        rations = character_inventory.get("rations", 0)

        member = ctx.author
        if rations >= 1:
            # Deduct resources
            character_inventory["rations"] -= 1
            save_data(user_id, data)

            # Set the status to Resting
            data["characters"][active_character]["status"] = "Resting"
            save_data(user_id, data)

            # Assign the Resting role and remove others
            role = discord.utils.get(ctx.guild.roles, name="Resting")
            if role:
                # Remove other status roles if present
                for status in ["Exploring", "Idle"]:
                    status_role = discord.utils.get(ctx.guild.roles, name=status)
                    if status_role in member.roles:
                        await member.remove_roles(status_role)
                await member.add_roles(role)
                await ctx.send(f"{active_character} is now resting. Ration consumed.")
            else:
                await ctx.send("Role 'Resting' not found. Please create it.")
        else:
            # Even if resources are insufficient, still set the status to Resting
            data["characters"][active_character]["status"] = "Resting"
            save_data(user_id, data)

            # Assign the Resting role and remove others
            role = discord.utils.get(ctx.guild.roles, name="Resting")
            if role:
                # Remove other status roles if present
                for status in ["Exploring", "Idle"]:
                    status_role = discord.utils.get(ctx.guild.roles, name=status)
                    if status_role in member.roles:
                        await member.remove_roles(status_role)
                await member.add_roles(role)
                await ctx.send(f"{active_character} is now resting, but doesn't have enough resources. Add a level of exhaustion. No rations consumed.")
            else:
                await ctx.send("Role 'Resting' not found. Please create it.")
    else:
        await ctx.send("You don't have an active character. Please switch to one first.")

# Command for players to set their status to "Exploring"
@bot.command()
async def explore(ctx):
    user_id = str(ctx.author.id)
    data = load_data(user_id)

    active_character = data.get("active_character")
    if active_character:
        # Set the status to Exploring
        data["characters"][active_character]["status"] = "Exploring"
        save_data(user_id, data)

        # Assign the Exploring role
        member = ctx.author
        role = discord.utils.get(ctx.guild.roles, name="Exploring")
        if role:
            # Remove other status roles if present
            for status in ["Resting", "Idle"]:
                status_role = discord.utils.get(ctx.guild.roles, name=status)
                if status_role in member.roles:
                    await member.remove_roles(status_role)
            await member.add_roles(role)
            await ctx.send(f"{active_character} is now exploring.")
        else:
            await ctx.send("Role 'Exploring' not found. Please create it.")
    else:
        await ctx.send("You don't have an active character. Please switch to one first.")

# Command to give resources to the ship's inventory (rations/material)
@bot.command()
async def deposit(ctx, material, amount: int):
    # Load ship inventory
    ship_inventory = load_ship_inventory()

    # Validate material
    if material not in ship_inventory:
        await ctx.send("Invalid material! You can deposit either 'rations' or 'material'.")
        return

    # Deposit the material
    ship_inventory[material] += amount
    save_ship_inventory(ship_inventory)

    await ctx.send(f"Deposited {amount} {material} to the ship's inventory.")

# Command to take resources from the ship's inventory (rations/material)
@bot.command()
async def take(ctx, material, amount: int):
    # Load ship inventory
    ship_inventory = load_ship_inventory()

    # Validate material
    if material not in ship_inventory:
        await ctx.send("Invalid material! You can take either 'rations' or 'material'.")
        return

    # Check if there are enough resources
    if ship_inventory[material] >= amount:
        ship_inventory[material] -= amount
        # Update the user's character's inventory
        user_id = str(ctx.author.id)
        data = load_data(user_id)
        active_character = data.get("active_character")
        if active_character:
            character_inventory = data["characters"][active_character].get("inventory", {})
            character_inventory[material] += amount
            save_data(user_id, data)
        save_ship_inventory(ship_inventory)

        await ctx.send(f"Took {amount} {material} from the ship's inventory.")
    else:
        await ctx.send("Not enough material in the ship's inventory.")

# Command to adjust a character's inventory
@bot.command()
async def adjust(ctx, action, material, amount: int):
    user_id = str(ctx.author.id)
    data = load_data(user_id)

    active_character = data.get("active_character")
    if not active_character:
        await ctx.send("You don't have an active character. Please switch to one first.")
        return

    # Validate material type
    if material not in ['rations', 'material']:
        await ctx.send("Invalid material! You can adjust 'rations' or 'material'.")
        return

    # Check the action (add or remove)
    if action not in ['add', 'remove']:
        await ctx.send("Invalid action! You can either 'add' or 'remove' materials.")
        return

    # Adjust the inventory
    character_inventory = data["characters"][active_character].get("inventory", {})

    if action == 'add':
        character_inventory[material] += amount
        await ctx.send(f"Added {amount} {material} to your character's inventory.")
    elif action == 'remove':
        if character_inventory[material] >= amount:
            character_inventory[material] -= amount
            await ctx.send(f"Removed {amount} {material} from your character's inventory.")
        else:
            await ctx.send(f"Not enough {material} in your inventory to remove.")
    
    save_data(user_id, data)

# Command to view the active character's inventory
@bot.command()
async def inventory(ctx):
    user_id = str(ctx.author.id)
    data = load_data(user_id)

    active_character = data.get("active_character")
    if active_character:
        character_inventory = data["characters"][active_character].get("inventory", {})
        inventory_str = (
            f"Inventory of {active_character}:\n"
            f"Rations: {character_inventory.get('rations', 0)}\n"
            f"Material: {character_inventory.get('material', 0)}"
        )
        await ctx.send(inventory_str)
    else:
        await ctx.send("You don't have an active character. Please switch to one first.")

# Command to view the ship's inventory
@bot.command()
async def ship_inventory(ctx):
    # Load ship inventory
    ship_inventory = load_ship_inventory()

    inventory_str = (
        f"Ship Inventory:\n"
        f"Rations: {ship_inventory.get('rations', 0)}\n"
        f"Material: {ship_inventory.get('material', 0)}"
    )
    await ctx.send(inventory_str)


# Run the bot
bot.run(TOKEN)
