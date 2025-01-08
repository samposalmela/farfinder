import discord
from discord.ext import commands
from utils.data_utils import load_data, save_data, load_ship_inventory, save_ship_inventory

class InventoryCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def inventory(self, ctx):
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

    @commands.command()
    async def ship_inventory(self, ctx):
        inventory = load_ship_inventory()
        inventory_str = "\n".join([f"{item.capitalize()}: {quantity}" for item, quantity in inventory.items()])
        response = (
            f"**Ship Inventory:**\n"
            f"{inventory_str if inventory else 'The ship inventory is empty.'}"
        )
        await ctx.send(response)

    @commands.command()
    async def adjust(self, ctx, action, material, amount: int):  # Fixed indentation
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
        character_inventory[material] = character_inventory.get(material, 0)  # Ensure default value is 0

        if action == 'add':
            character_inventory[material] += amount
            await ctx.send(f"Added {amount} {material} to your character's inventory.")
        elif action == 'remove':
            if character_inventory[material] >= amount:
                character_inventory[material] -= amount
                await ctx.send(f"Removed {amount} {material} from your character's inventory.")
            else:
                await ctx.send(f"Not enough {material} in your inventory to remove.")

        data["characters"][active_character]["inventory"] = character_inventory
        save_data(user_id, data)

async def setup(bot):
    await bot.add_cog(InventoryCommands(bot))
