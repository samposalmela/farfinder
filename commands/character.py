import discord
from discord.ext import commands
from utils.data_utils import load_data, save_data
from utils.role_utils import manage_status_roles

class CharacterCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def character(self, ctx):
        """
        Main command group for character-related operations.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid character command! Use `register`, `switch`, `profile`, or `inventory`.")

    @character.command()
    async def register(self, ctx, character_name, character_class, species, background, description=""):
        """
        Registers a new character.
        """
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
            "inventory": {'rations': 0, 'material': 0, 'tokens': 0}  # Include tokens
        }
        save_data(user_id, data)
        await ctx.send(f"Character {character_name} registered successfully!")

    @character.command()
    async def switch(self, ctx, character_name):
        """
        Switches to the specified character and updates the user's nickname in the server.
        """
        user_id = str(ctx.author.id)
        data = load_data(user_id)

        if character_name in data["characters"]:
            # Switch to the new character
            data["active_character"] = character_name
            save_data(user_id, data)

            # Change the user's nickname to match the character's name
            member = ctx.author
            try:
                # Check if the bot has the 'Manage Nicknames' permission
                if ctx.channel.permissions_for(member.guild.me).manage_nicknames:
                    # Attempt to change the nickname
                    await member.edit(nick=character_name)
                    await ctx.send(f"Switched to character {character_name} and updated your nickname to {character_name}.")
                else:
                    await ctx.send(f"Switched to character {character_name}, but I don't have permission to change your nickname.")
            except discord.Forbidden:
                # Log and notify the user if the bot doesn't have permission
                await ctx.send(f"Switched to character {character_name}, but I don't have the required permissions to change your nickname.")
                print(f"Permission to change nickname denied for {member.name} in server {member.guild.name}.")
            except Exception as e:
                # Log any other errors that occur
                await ctx.send(f"An error occurred while trying to change your nickname: {e}")
                print(f"Error changing nickname for {member.name}: {e}")
        else:
            await ctx.send("Character not found. Please register the character first.")

    @character.command()
    async def profile(self, ctx, character_name=None):
        """
        Views the profile of the active character or any character by name.
        """
        user_id = str(ctx.author.id)
        data = load_data(user_id)

        # If no character_name is provided, use the active character
        character_name = character_name or data.get("active_character")

        if character_name:
            character_info = data["characters"].get(character_name)
            if character_info:
                profile_str = (
                    f"Name: {character_name}\n"
                    f"Class: {character_info['class']}\n"
                    f"Species: {character_info['species']}\n"
                    f"Background: {character_info['background']}\n"
                    f"Level: {character_info['level']}\n"
                    f"Status: {character_info['status']}\n"
                    f"Description: {character_info['description'] if character_info['description'] else 'No description set.'}"
                )
                await ctx.send(profile_str)
            else:
                await ctx.send(f"Character {character_name} not found.")
        else:
            await ctx.send("You don't have an active character. Please switch to one first.")

    @character.group()
    async def inventory(self, ctx):
        """
        Subcommand group for inventory-related operations.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid inventory command! Use `view`, `adjust`, `take`, or `deposit`.")

    @inventory.command()
    async def view(self, ctx):
        """
        Views the current inventory of the active character.
        """
        user_id = str(ctx.author.id)
        data = load_data(user_id)

        active_character = data.get("active_character")
        if active_character:
            inventory = data["characters"][active_character]["inventory"]
            inventory_str = "\n".join([f"{item.capitalize()}: {quantity}" for item, quantity in inventory.items()])
            response = (
                f"**{active_character}'s Inventory:**\n"
                f"{inventory_str if inventory else 'No items in inventory.'}"
            )
            await ctx.send(response)
        else:
            await ctx.send("No active character selected.")

    @inventory.command()
    async def adjust(self, ctx, material, amount: int):
        """
        Adjusts the inventory for the active character.
        """
        user_id = str(ctx.author.id)
        data = load_data(user_id)

        active_character = data.get("active_character")
        if not active_character:
            await ctx.send("You don't have an active character. Please switch to one first.")
            return

        if material not in ['rations', 'material', 'tokens']:
            await ctx.send("Invalid material! You can adjust 'rations', 'material', or 'tokens'.")
            return

        character_inventory = data["characters"][active_character].get("inventory", {})
        character_inventory[material] = character_inventory.get(material, 0) + amount

        if character_inventory[material] < 0:
            await ctx.send(f"Not enough {material} in your inventory to remove.")
            return

        data["characters"][active_character]["inventory"] = character_inventory
        save_data(user_id, data)

        action = "Added" if amount > 0 else "Removed"
        await ctx.send(f"{action} {abs(amount)} {material} to your inventory.")

    @character.command()
    async def status(self, ctx, new_status):
        """
        Updates the active character's status.
        """
        user_id = str(ctx.author.id)
        data = load_data(user_id)

        active_character = data.get("active_character")
        if not active_character:
            await ctx.send("You don't have an active character. Please switch to one first.")
            return

        valid_statuses = ["Idle", "Resting", "Exploring"]
        if new_status not in valid_statuses:
            await ctx.send(f"Invalid status! Choose from: {', '.join(valid_statuses)}.")
            return

        if new_status == "Resting":
            inventory = data["characters"][active_character]["inventory"]
            if inventory.get("rations", 0) < 1:
                await ctx.send(f"{active_character} does not have enough rations to rest.")
                return
            inventory["rations"] -= 1

        data["characters"][active_character]["status"] = new_status
        save_data(user_id, data)
        await manage_status_roles(ctx, new_status)
        await ctx.send(f"{active_character} is now {new_status.lower()}.")

    @character.command()
    async def list(self, ctx):
        """
        Lists all registered characters.
        """
        user_id = str(ctx.author.id)
        data = load_data(user_id)

        characters = data["characters"]
        character_list = [name for name in characters]
        await ctx.send(f"Your characters: {', '.join(character_list) if character_list else 'None'}")

    @character.command()
    async def edit(self, ctx, character_name, field, *, value):
        """
        Edits a character's details (class, species, background, level, description).
        """
        user_id = str(ctx.author.id)
        data = load_data(user_id)

        if character_name not in data["characters"]:
            await ctx.send(f"Character {character_name} not found.")
            return

        valid_fields = ["class", "species", "background", "level", "description"]
        if field not in valid_fields:
            await ctx.send(f"Invalid field! Choose from: {', '.join(valid_fields)}.")
            return

        if field == "level":
            try:
                value = int(value)
                if value < 1:
                    await ctx.send("Level must be 1 or higher.")
                    return
            except ValueError:
                await ctx.send("Level must be a number.")
                return

        data["characters"][character_name][field] = value
        save_data(user_id, data)
        await ctx.send(f"Updated {character_name}'s {field} to {value}.")

async def setup(bot):
    await bot.add_cog(CharacterCommands(bot))
