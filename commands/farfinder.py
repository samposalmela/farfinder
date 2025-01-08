import discord
from discord.ext import commands
from utils.data_utils import load_ship_inventory, save_ship_inventory, load_data, save_data

class FarfinderCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def farfinder(self, ctx):
        """
        Main command group for Farfinder-related operations.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid Farfinder command! Use `inventory` or `resources`.")

    @farfinder.group()
    async def inventory(self, ctx):
        """
        Subcommand group for inventory-related operations.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid inventory command! Use `take`, `deposit`, or `view`.")

    @inventory.command()
    async def deposit(self, ctx, material, amount: int):
        """
        Deposits materials into the Farfinder inventory.
        """
        farfinder_inventory = load_ship_inventory()

        if material not in farfinder_inventory:
            await ctx.send("Invalid material! You can deposit 'rations' or 'material'.")
            return

        # Update Farfinder inventory
        farfinder_inventory[material] += amount
        save_ship_inventory(farfinder_inventory)

        # Update character inventory
        user_id = str(ctx.author.id)
        data = load_data(user_id)
        active_character = data.get("active_character")

        if active_character:
            character_inventory = data["characters"][active_character].get("inventory", {})
            character_inventory[material] = character_inventory.get(material, 0) + amount
            data["characters"][active_character]["inventory"] = character_inventory
            save_data(user_id, data)

        await ctx.send(f"Deposited {amount} {material} to the Farfinder's inventory.")

    @inventory.command()
    async def take(self, ctx, material, amount: int):
        """
        Takes materials from the Farfinder inventory.
        """
        farfinder_inventory = load_ship_inventory()

        if material not in farfinder_inventory:
            await ctx.send("Invalid material! You can take 'rations' or 'material'.")
            return

        if farfinder_inventory[material] >= amount:
            farfinder_inventory[material] -= amount

            user_id = str(ctx.author.id)
            data = load_data(user_id)
            active_character = data.get("active_character")

            if active_character:
                character_inventory = data["characters"][active_character].get("inventory", {})
                character_inventory[material] = character_inventory.get(material, 0) + amount
                data["characters"][active_character]["inventory"] = character_inventory
                save_data(user_id, data)

            save_ship_inventory(farfinder_inventory)
            await ctx.send(f"Took {amount} {material} from the Farfinder's inventory.")
        else:
            await ctx.send(f"Not enough {material} in the Farfinder's inventory.")

    @inventory.command()
    async def view(self, ctx):
        """
        Views the current Farfinder inventory.
        """
        farfinder_inventory = load_ship_inventory()
        inventory_str = "\n".join([f"{item.capitalize()}: {quantity}" for item, quantity in farfinder_inventory.items()])
        response = f"**Farfinder Inventory:**\n{inventory_str if inventory_str else 'The inventory is empty.'}"
        await ctx.send(response)

async def setup(bot):
    await bot.add_cog(FarfinderCommands(bot))
