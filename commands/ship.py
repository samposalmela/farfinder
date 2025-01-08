import discord
from discord.ext import commands
from utils.data_utils import load_ship_inventory, save_ship_inventory, load_data, save_data

class ShipCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def deposit(self, ctx, material, amount: int):
        ship_inventory = load_ship_inventory()

        if material not in ship_inventory:
            await ctx.send("Invalid material! You can deposit 'rations' or 'material'.")
            return

        # Update ship inventory
        ship_inventory[material] += amount
        save_ship_inventory(ship_inventory)

        # Update character inventory
        user_id = str(ctx.author.id)
        data = load_data(user_id)
        active_character = data.get("active_character")

        if active_character:
            character_inventory = data["characters"][active_character].get("inventory", {})
            character_inventory[material] = character_inventory.get(material, 0) - amount
            data["characters"][active_character]["inventory"] = character_inventory
            save_data(user_id, data)

        await ctx.send(f"Deposited {amount} {material} to the ship's inventory.")

    @commands.command()
    async def take(self, ctx, material, amount: int):
        ship_inventory = load_ship_inventory()

        if material not in ship_inventory:
            await ctx.send("Invalid material! You can take 'rations' or 'material'.")
            return

        if ship_inventory[material] >= amount:
            ship_inventory[material] -= amount

            user_id = str(ctx.author.id)
            data = load_data(user_id)
            active_character = data.get("active_character")

            if active_character:
                character_inventory = data["characters"][active_character].get("inventory", {})
                character_inventory[material] = character_inventory.get(material, 0) + amount
                data["characters"][active_character]["inventory"] = character_inventory
                save_data(user_id, data)

            save_ship_inventory(ship_inventory)
            await ctx.send(f"Took {amount} {material} from the ship's inventory.")
        else:
            await ctx.send(f"Not enough {material} in the ship's inventory.")

async def setup(bot):
    await bot.add_cog(ShipCommands(bot))
